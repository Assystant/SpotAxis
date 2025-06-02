All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of the author nor the names of other
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Description: ==========
        Mots vides
        ==========
        
        |travis-develop| |coverage-develop|
        
        Python library for managing common stop words in 39 languages.
        
        .. contents::
        
        Usage
        =====
        
        Simple
        ------
        
        Better than a long speech, here a direct introduction: ::
        
          >>> from mots_vides import stop_words
        
          >>> english_stop_words = stop_words('en')
          >>> text = """
          ... Even though using "lorem ipsum" often arouses curiosity
          ... due to its resemblance to classical Latin,
          ... it is not intended to have meaning.
          ... """
        
          >>> print(english_stop_words.rebase(text))
          XXXX XXXXXX XXXXX "lorem ipsum" XXXXX arouses curiosity
          XXX XX XXX resemblance XX classical Latin,
          XX XX XXX intended XX XXXX meaning.
        
          >>> print(english_stop_words.rebase(text, '').split())
          ['"lorem', 'ipsum"', 'arouses', 'curiosity', 'resemblance',
          'classical', 'Latin,', 'intended', 'meaning.']
        
        Advanced
        --------
        
        *Mots vides* also provides two classes for managing the stop words in your
        language.
        
        ``StopWord`` which is a container for a collection of stop words.
        By default is language agnostic, but can be easily manipulated to create
        the collection: ::
        
          >>> from mots_vides import StopWord
        
          >>> french_stop_words = StopWord('french', ['le', 'la', 'les'])
          >>> french_stop_words += StopWord('french', ['un', 'une', 'des'])
          >>> french_stop_words += ['or', 'ni', 'car']
          >>> french_stop_words += 'assez'
          >>> french_stop_words += u'aussitôt'
          >>> print(sorted(french_stop_words))
          ['assez', u'aussitôt', 'car', 'des', 'la', 'le', 'les', 'ni', 'or', 'un', 'une']
        
        ``StopWordFactory`` is a factory for initializing ``StopWord`` objects by
        language and the appropriate collection of stop words. ::
        
          >>> from mots_vides import StopWordFactory
        
          >>> factory = StopWordFactory()
          >>> french_stop_words = factory.get_stop_words('french')
          >>> print(len(french_stop_words))
          577
        
        You can also use international language code to query a collection: ::
        
          >>> french_stop_words = factory.get_stop_words('fr')
          >>> print(len(french_stop_words))
          577
        
        If the required language does not exist a ``StopWordError`` is raised,
        unless the ``fail_safe`` parameter is set to ``True``: ::
        
          >>> klingon_stop_words = factory.get_stop_words('klingon')
          StopWordError: Stop words are not available in "klingon".
          >>> klingon_stop_words = factory.get_stop_words('klingon', fail_safe=True)
          >>> print(len(klingon_stop_words))
          0
        
        Supported languages
        ===================
        
        * Arabic
        * Armenian
        * Basque
        * Bengali
        * Bulgarian
        * Catalan
        * Chinese
        * Czech
        * Danish
        * Dutch
        * English
        * Finnish
        * French
        * Galician
        * German
        * Greek
        * Hindi
        * Hungarian
        * Indonesian
        * Irish
        * Italian
        * Japanese
        * Korean
        * Latvian
        * Lithuanian
        * Marathi
        * Norwegian
        * Persian
        * Polish
        * Portuguese
        * Romanian
        * Russian
        * Slovak
        * Spanish
        * Swedish
        * Thai
        * Turkish
        * Ukrainian
        * Urdu
        
        Compatibility
        =============
        
        Tested with Python 2.6, 2.7, 3.2, 3.3, 3.4.
        
        Authors
        =======
        
        * https://github.com/Fantomas42
        * https://github.com/chrisdavisgithub
        
        Notes
        =====
        
        *Mots vides* means *stop words* in french.
        
        Inspired from https://github.com/Alir3z4/python-stop-words
        
        Changelog
        =========
        
        2015.2.6
        --------
        
        - Fix potential issue in factory.get_available_languages
        
        2015.2.5
        --------
        
        - Fix packaging
        - Add a rebaser command script
        
        2015.2.4
        --------
        
        - Initial release
        
        2015.1.21.dev0
        --------------
        
        - Development release
        
        .. |travis-develop| image:: https://travis-ci.org/Fantomas42/mots-vides.png?branch=develop
           :alt: Build Status - develop branch
           :target: http://travis-ci.org/Fantomas42/mots-vides
        .. |coverage-develop| image:: https://coveralls.io/repos/Fantomas42/mots-vides/badge.png?branch=develop
           :alt: Coverage of the code
           :target: https://coveralls.io/r/Fantomas42/mots-vides
        
Keywords: stop,words,text,parsing
Platform: UNKNOWN
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 3
Classifier: Intended Audience :: Developers
Classifier: Operating System :: OS Independent
Classifier: License :: OSI Approved :: BSD License
Classifier: Topic :: Software Development :: Libraries :: Python Modules
