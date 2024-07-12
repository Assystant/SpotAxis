from activities.models import *

def post_notification(user=None, actor = None, action = None, target = None, target_action = None, subject = None, subject_action = None, msg=None, url=None, message_chunks = []):
	notification = Notification.objects.create(user = user , message = msg, action_url = url, actor=actor, action = action, target = target, target_action = target_action, subject = subject, subject_action = subject_action)
	print(notification)
	for order,message_chunk in enumerate(message_chunks):
		chunk = MessageChunk.objects.create(subject = message_chunk['subject'], subject_action = message_chunk['subject_action'], action_url = message_chunk['action_url'] ,order = order)
		notification.message_chunks.add(chunk)

def post_org_notification(user=None,actor=None, msg=None, url=None, action = None, target = None, target_action = None, subject = None, subject_action = None, message_chunks = []):
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