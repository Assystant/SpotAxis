"""
Comparison tools for Zinnia

This module provides tools for comparing blog entries based on their textual
content, using vector models and Pearson correlation to compute similarities.

Features include:
- Vectorization of model fields (e.g., title + content)
- Text cleaning (punctuation, stopword removal)
- Pearson correlation score computation
- High-level caching for performance
- Site-aware caching for multi-site support

Main classes:
- `ModelVectorBuilder`: Builds a raw word vector dataset from queryset.
- `CachedModelVectorBuilder`: Adds caching on top of vector builder.
- `EntryPublishedVectorBuilder`: Specific to published blog entries.
"""

from math import sqrt
from django.contrib.sites.models import Site
from django.core.cache import InvalidCacheBackendError, caches
from django.utils import six
from django.utils.functional import cached_property
from django.utils.html import strip_tags

import regex as re

from zinnia.models.entry import Entry
from zinnia.settings import COMPARISON_FIELDS, STOP_WORDS

# Regex to strip punctuation
PUNCTUATION = re.compile(r'\p{P}+')

def pearson_score(list1, list2):
    """
    Compute Pearson correlation coefficient between two equal-length lists.

    Returns a float between -1 (negatively correlated) and 1 (positively correlated).

    Args:
        list1 (list of float/int): First vector
        list2 (list of float/int): Second vector

    Returns:
        float: Pearson score
    """
    size = len(list1)
    sum1, sum2 = sum(list1), sum(list2)
    sum_sq1 = sum([x ** 2 for x in list1])
    sum_sq2 = sum([x ** 2 for x in list2])
    prod_sum = sum([list1[i] * list2[i] for i in range(size)])

    num = prod_sum - (sum1 * sum2 / float(size))
    den = sqrt((sum_sq1 - sum1 ** 2 / size) * (sum_sq2 - sum2 ** 2 / size))

    return num / den if den != 0 else 0


class ModelVectorBuilder(object):
    """
    Builds word-frequency vectors from a queryset to compare objects.

    Attributes:
        limit (int): Max number of items to include.
        fields (list): List of field names to extract text from.
        queryset (QuerySet): The queryset of objects to analyze.
    """

    limit = None
    fields = None
    queryset = None

    def __init__(self, **kwargs):
        self.limit = kwargs.pop('limit', self.limit)
        self.fields = kwargs.pop('fields', self.fields)
        self.queryset = kwargs.pop('queryset', self.queryset)

    def get_related(self, instance, number):
        """
        Get the top `number` related objects to a given instance.

        Returns:
            list: Related model instances
        """
        related_pks = self.compute_related(instance.pk)[:number]
        related_pks = [pk for pk, _ in related_pks]
        related_objects = sorted(
            self.queryset.model.objects.filter(pk__in=related_pks),
            key=lambda x: related_pks.index(x.pk))
        return related_objects

    def compute_related(self, object_id, score=pearson_score):
        """
        Compute a sorted list of (pk, similarity_score) tuples.

        Returns:
            list of tuple: Most similar objects to given object_id
        """
        dataset = self.dataset
        object_vector = dataset.get(object_id)
        if not object_vector:
            return []

        object_related = {}
        for o_id, o_vector in dataset.items():
            if o_id != object_id:
                try:
                    object_related[o_id] = score(object_vector, o_vector)
                except ZeroDivisionError:
                    continue

        return sorted(object_related.items(), key=lambda x: x[1], reverse=True)

    @cached_property
    def raw_dataset(self):
        """
        Raw token dataset from queryset and fields.

        Returns:
            dict: {pk: [list of words]}
        """
        dataset = {}
        qs = self.queryset.values_list(*(['pk'] + self.fields))
        if self.limit:
            qs = qs[:self.limit]

        for item in qs:
            item = list(item)
            pk = item.pop(0)
            text = ' '.join(map(six.text_type, item))
            dataset[pk] = self.raw_clean(text)

        return dataset

    def raw_clean(self, text):
        """
        Clean text by stripping HTML, stopwords, punctuation, and lowercasing.

        Returns:
            list: Cleaned list of words
        """
        text = strip_tags(text)
        text = STOP_WORDS.rebase(text, '')  # Remove stop words
        text = PUNCTUATION.sub('', text)
        text = text.lower()
        return [word for word in text.split() if len(word) > 1]

    @cached_property
    def columns_dataset(self):
        """
        Construct full vector dataset and its word columns.

        Returns:
            tuple: (columns, {pk: vector})
        """
        data = {}
        word_totals = {}

        for pk, words in self.raw_dataset.items():
            word_counts = {}
            for word in words:
                word_totals[word] = word_totals.get(word, 0) + 1
                word_counts[word] = word_counts.get(word, 0) + 1
            data[pk] = word_counts

        # Use the most common words (top 250) as vector dimensions
        columns = sorted(
            sorted(word_totals.keys()),
            key=lambda w: word_totals[w],
            reverse=True)[:250]

        dataset = {
            pk: [data[pk].get(word, 0) for word in columns]
            for pk in data
        }

        return columns, dataset

    @property
    def columns(self):
        """
        Return the vector dimensions (vocabulary).

        Returns:
            list of str: List of words used as vector columns
        """
        return self.columns_dataset[0]

    @property
    def dataset(self):
        """
        Return the final vector dataset.

        Returns:
            dict: {pk: vector}
        """
        return self.columns_dataset[1]


class CachedModelVectorBuilder(ModelVectorBuilder):
    """
    Adds caching to avoid recomputing vectors or comparisons repeatedly.
    """

    @property
    def cache_backend(self):
        """
        Returns the cache configured as 'comparison', or 'default' fallback.
        """
        try:
            return caches['comparison']
        except InvalidCacheBackendError:
            return caches['default']

    @property
    def cache_key(self):
        """
        Cache key used to store the vector dataset and results.

        Returns:
            str
        """
        return self.__class__.__name__

    def get_cache(self):
        return self.cache_backend.get(self.cache_key, {})

    def set_cache(self, value):
        updated = {**self.cache, **value}
        self.cache_backend.set(self.cache_key, updated)

    cache = property(get_cache, set_cache)

    def cache_flush(self):
        """
        Flush all cached data for this vector builder.
        """
        self.cache_backend.delete(self.cache_key)

    def get_related(self, instance, number):
        """
        Cached version of get_related.
        """
        key = f'{instance.pk}:{number}'
        if key not in self.cache:
            self.cache = {key: super().get_related(instance, number)}
        return self.cache[key]

    @property
    def columns_dataset(self):
        """
        Cached version of columns_dataset property.
        """
        key = 'columns_dataset'
        if key not in self.cache:
            self.cache = {key: super().columns_dataset}
        return self.cache[key]


class EntryPublishedVectorBuilder(CachedModelVectorBuilder):
    """
    Vector builder specific to Zinnia's published entries.

    Uses a queryset of only published entries and fields from settings.
    Limits to 100 entries by default.
    """
    limit = 100
    queryset = Entry.published
    fields = COMPARISON_FIELDS

    @property
    def cache_key(self):
        """
        Cache key includes the site ID to support multi-site setup.
        """
        return f'{super().cache_key}:{Site.objects.get_current().pk}'
