"""
Utility functions for managing activities and notifications in the SpotAxis application.

This module provides helper functions for creating and managing activities and notifications
across the system. It handles the creation of notifications, organizational notifications,
and various types of activities with their associated message chunks.
"""

from __future__ import absolute_import
from __future__ import print_function
from activities.models import *

def post_notification(user=None, actor = None, action = None, target = None, target_action = None, subject = None, subject_action = None, msg=None, url=None, message_chunks = []):
	"""
	Creates a notification for a specific user with optional message chunks.
	
	Args:
		user (User, optional): The user to receive the notification.
		actor (User, optional): The user who triggered the notification.
		action (str, optional): The type of action that occurred.
		target (User, optional): The target user of the action.
		target_action (str, optional): Action associated with the target.
		subject (str, optional): The subject of the notification.
		subject_action (str, optional): Action associated with the subject.
		msg (str, optional): The main notification message.
		url (str, optional): URL associated with the notification.
		message_chunks (list, optional): List of dictionaries containing message chunk data.
			Each chunk should have 'subject', 'subject_action', and 'action_url' keys.
	"""
	notification = Notification.objects.create(user = user , message = msg, action_url = url, actor=actor, action = action, target = target, target_action = target_action, subject = subject, subject_action = subject_action)
	print(notification)
	for order,message_chunk in enumerate(message_chunks):
		chunk = MessageChunk.objects.create(subject = message_chunk['subject'], subject_action = message_chunk['subject_action'], action_url = message_chunk['action_url'] ,order = order)
		notification.message_chunks.add(chunk)

def post_org_notification(user=None,actor=None, msg=None, url=None, action = None, target = None, target_action = None, subject = None, subject_action = None, message_chunks = []):
	"""
	Creates notifications for multiple users in an organization.
	
	This function handles sending notifications to all members of an organization,
	excluding the actor who triggered the notification. It can either notify all
	members of a company or a specific subset of users.
	
	Args:
		user (str|User|QuerySet, optional): 
			- 'all' or None: Notifies all company members
			- User or QuerySet: Specific users to notify
		actor (User): The user who triggered the notification.
		msg (str, optional): The main notification message.
		url (str, optional): URL associated with the notification.
		action (str, optional): The type of action that occurred.
		target (User, optional): The target user of the action.
		target_action (str, optional): Action associated with the target.
		subject (str, optional): The subject of the notification.
		subject_action (str, optional): Action associated with the subject.
		message_chunks (list, optional): List of message chunk dictionaries.
	"""
	if user == 'all' or user == None:
		company = actor.recruiter.company.all()[0]
		users = [r.user for r in company.recruiter_set.all()]
		if actor in users:
			users.remove(actor)
	else:
		users = user
		try:
			users = users.exclude(id = actor.id)
		except:
			pass
		try:
			users = users.remove(actor)
		except:
			pass
	print(users)
	for member in users:
		post_notification(user=member, actor = actor, msg = msg, url = url, target = target, subject = subject, action = action, target_action = target_action, subject_action = subject_action, message_chunks = message_chunks)

def post_activity(actor = None, action = None, message = None, subscribers=[], action_url = "", activity_type = 0, target = None, target_action = None, subject = None, subject_action = None, postulate_id = None, message_chunks=[]):
	"""
	Creates and manages activities in the system with associated notifications.
	
	This function handles the creation of different types of activities (normal and postulate-related)
	and manages their subscribers and notifications. It supports two main activity types:
	- Type 0: Standard activity
	- Type 1: Postulate-related activity
	
	Args:
		actor (User, optional): The user who performed the activity.
		action (str, optional): The type of action performed.
		message (str, optional): The main activity message.
		subscribers (list, optional): List of users to subscribe to the activity.
		action_url (str, optional): URL associated with the activity.
		activity_type (int, optional): Type of activity (0 for standard, 1 for postulate).
		target (User, optional): The target user of the activity.
		target_action (str, optional): Action associated with the target.
		subject (str, optional): The subject of the activity.
		subject_action (str, optional): Action associated with the subject.
		postulate_id (int, optional): ID of the associated postulate for type 1 activities.
		message_chunks (list, optional): List of message chunk dictionaries.
	
	Note:
		For activity_type 1 (postulate-related):
		- If an activity already exists for the postulate, it adds new subscribers
		- If no activity exists, it creates a new one with appropriate subscribers
		- Subscribers include postulate vacancy company recruiters with membership level 3
	"""
	try:
		company = actor.recruiter.company.all()[0]
	except:
		company = None
	if activity_type == 0 or not activity_type:
		activity = Activity.objects.create(actor = actor, message = message, action_url = action_url, action = action, activity_type = 0)
		order = 0;
		for message_chunk in message_chunks:
			chunk = MessageChunk.objects.create(subject = message_chunk['subject'], subject_action = message_chunk['subject_action'], action_url = message_chunk['action_url'] ,order = order)
			activity.message_chunks.add(chunk)
			order = order + 1 
			# raise ValueError(activity.message_chunks.all())
		if actor:
			for subscriber in subscribers:
				activity.subscribers.add(subscriber)
				activity.subscribers.add(actor)
		if not activity.action_url:
			activity.action_url = activity.get_absolute_url()
		activity.save()
		try:
			subscribers = subscribers.exclude(user = request.user)
		except:
			if actor in subscribers:
				subscribers = subscribers.remove(actor)
		post_org_notification(message_chunks = message_chunks, user = subscribers, subject = subject, subject_action = subject_action, target = target, target_action = target_action, msg = message, actor = actor, action = action, url = action_url)
		# raise ValueError(order)
	elif activity_type == 1:
		try:
			activity = Activity.objects.get(postulate__id = postulate_id)
		except:
			activity = None
		if activity:
			for subscriber in subscribers:
				activity.subscribers.add(subscriber)
			activity.save()
			post_org_notification(message_chunks = message_chunks, user = activity.subscribers.all(), msg = message, action = action, actor = actor, subject = subject, subject_action = subject_action, target_action = target_action, target = target)
			# for subscriber in activity.subscribers:
			# 	post_notification(user = subscriber, msg = action, url = activity.action_url, actor = actor)
		else:
			postulate = Postulate.objects.get(id = postulate_id)
			activity = Activity.objects.create(actor = actor, message = message, action = action, activity_type = activity_type,postulate = postulate, action_url = action_url)
			for user in [p.user for p in postulate.vacancy.company.recruiter_set.filter(membership=3)]:
				activity.subscribers.add(user)
			if company and actor:
				activity.subscribers.add(actor)
			activity.save()
			post_org_notification(message_chunks = message_chunks, user = activity.subscribers.all(), actor = actor, msg = message, url = action_url, subject = subject, subject_action = subject_action, target_action = target_action, target = target, action = action)

	# elif activity_type == 2:
	# 	public_postulate = Public_Postulate.objects.get(id = postulate_id)
	# 	try:
	# 		activity = Activity.objects.get(public_postulate = public_postulate)
	# 	except:
	# 		activity = None
	# 	if activity:
	# 		for subscriber in subscribers:
	# 			activity.subscribers.add(subscriber)
	# 		activity.save()
	# 		post_org_notification(message_chunks = message_chunks, user = activity.subscribers.all(), msg = message, action = action, actor = actor, subject = subject, subject_action = subject_action, target_action = target_action, target = target)
	# 		# for subscriber in activity.subscribers:
	# 		# 	post_notification(user = subscriber, msg = action, url = activity.action_url, actor = actor)
	# 	else:
	# 		if public_postulate.recruiter:
	# 			subscribers = subscribers  + [public_postulate.recruiter.user]
	# 		activity = Activity.objects.create(actor = actor, message = message, action = action, activity_type = activity_type, public_postulate = public_postulate, action_url = action_url)
	# 		for user in [p.user for p in public_postulate.vacancy.company.recruiter_set.filter(membership=3)]:
	# 			activity.subscribers.add(user)
	# 		if company and actor:
	# 			activity.subscribers.add(actor)
	# 		activity.save()
	# 		post_org_notification(message_chunks = message_chunks, user = activity.subscribers.all(), actor = actor, msg = message, url = action_url, subject = subject, subject_action = subject_action, target_action = target_action, target = target, action = action)