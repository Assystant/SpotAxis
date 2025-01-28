
"""
 Testing Models that are defined under Common project.
 The test is divided into 2 parts:
 	1. Field properties
 	2. Model functions
 In this documentation values in ' ' represent actual value to be tested against.
 (s) represents singular
 (p) represents plural
 """

# Imports
from __future__ import absolute_import
from django.test import SimpleTestCase, TestCase
from common.models import Profile, User

## Testing Profile Model

class ProfileTest(SimpleTestCase):
	"""
	USE CASE
	--------------------
		1. Maximum length of both fields is '20'.
		2. Conversion of instance to string returns the name
		3. Verbose name is 'Profile' (s) or 'Profiles' (p)
	"""
	def test_profile_model_fields_max_length(self):
		"""Check max length of fields in Profile Model"""
		self.assertEqual(Profile._meta.get_field('name').max_length, 20)
		self.assertEqual(Profile._meta.get_field('codename').max_length, 20)

	def test_profile_model_verbose_names(self):
		"""Check verbose names of Profile Model"""
		self.assertEqual(Profile._meta.verbose_name, 'Profile')
		self.assertEqual(Profile._meta.verbose_name_plural, 'Profiles')

	def test_profile_model_string_output(self):
		"""Check string output of a Profile Model Instance"""
		name = 'random name !@#'
		profile = Profile(name = name, codename = 'codename')
		self.assertEqual(str(profile), name)

## Testing User Model

class UserTest(TestCase):
	"""
	USE CASE
	--------------------
		1. Fields:
			a. Maxlength - 
				i. username - '150'
				ii. first_name - '30'
				iii. last_name - '150'
				iv. photo - '200'
				v. logued_by - '2'
			b. Unique - 
				i. username (not unique)
				ii. email
			c. Verbose name - 
				i. username - 'Username'
				ii. first_name - 'First Name'
				iii. last_name - 'Last Name'
				iv. email - 'Email Address'
				v. is_staff - 'Staff Status'
				vi. is_active - 'Active'
				vii. date_joined - 'Date Joined'
				viii. profile - 'Profile'
				ix. phone - 'Phone'
				x. phone_ext - 'Extension'
				xi. cellphone - 'Celular'
				xii. photo - 'Photo'
				xiii. logued_by - 'Loggin Method'
			d. Default -
				i. is_staff - 'False'
				ii. is_active - 'True'
				iii. photo - 'PHOTO_USER_DEFAULT' 
			e. Choices - 
				i. logued_by - 'LOGIN_OPTIONS'
			f. USERNAME_FIELD is 'email'
		2. Verbose name is 'User' (s) or 'Users' (p)
		3. Conversion of instance to string returns the full_name
		4. Order Users in descending order based on date_joined
		5. get_full_name returns space seperated full name
		6. get_short_name returns only the first name
		7. get_remote_image opens a web image and stores it locally as the user's photo
		8. Username returns email
	"""
	def test_user_model_fields_max_length(self):
		"""Check max length of fields in User Model"""
		self.assertEqual(User._meta.get_field('_username').max_length, 150)
		self.assertEqual(User._meta.get_field('first_name').max_length, 30)
		self.assertEqual(User._meta.get_field('last_name').max_length, 150)
		self.assertEqual(User._meta.get_field('photo').max_length, 200)
		self.assertEqual(User._meta.get_field('logued_by').max_length, 2)

	def test_user_model_fields_unique(self):
		"""Check Unique requirements of User Model"""
		self.assertFalse(User._meta.get_field('_username').unique)
		self.assertTrue(User._meta.get_field('email').unique)

	def test_user_model_verbose_names(self):
		"""Check verbose names of User Model"""
		self.assertEqual(User._meta.verbose_name, 'User')
		self.assertEqual(User._meta.verbose_name_plural, 'Users')
		self.assertEqual(User._meta.get_field('_username').verbose_name, 'Username')
		self.assertEqual(User._meta.get_field('first_name').verbose_name, 'First Name')
		self.assertEqual(User._meta.get_field('last_name').verbose_name, 'Last Name')
		self.assertEqual(User._meta.get_field('email').verbose_name, 'Email Address')
		self.assertEqual(User._meta.get_field('is_staff').verbose_name, 'Staff Status')
		self.assertEqual(User._meta.get_field('is_active').verbose_name, 'Active')
		self.assertEqual(User._meta.get_field('date_joined').verbose_name, 'Date Joined')
		self.assertEqual(User._meta.get_field('profile').verbose_name, 'Profile')
		self.assertEqual(User._meta.get_field('phone').verbose_name, 'Phone')
		self.assertEqual(User._meta.get_field('phone_ext').verbose_name, 'Extension')
		self.assertEqual(User._meta.get_field('cellphone').verbose_name, 'Celular')
		self.assertEqual(User._meta.get_field('photo').verbose_name, 'Photo')
		self.assertEqual(User._meta.get_field('logued_by').verbose_name, 'Loggin Method')

	def test_user_model_field_defaults(self):
		"""Checks default values for fields in User Model"""
		self.assertEqual(User._meta.get_field('is_staff').default, False)
		self.assertEqual(User._meta.get_field('is_active').default, True)
		from TRM.settings import PHOTO_USER_DEFAULT
		self.assertEqual(User._meta.get_field('photo').default, PHOTO_USER_DEFAULT)

	def test_user_model_field_choices(self):
		from common.models import LOGIN_OPTIONS
		self.assertEqual(User._meta.get_field('logued_by').choices, LOGIN_OPTIONS)

	def test_user_model_string_output(self):
		"""Check string output of a User Model Instance"""
		first_name = 'fname'
		last_name = 'lname'
		email = 'email@email.email'
		profile = Profile(name="Onsite", codename="OS")
		user = User(email=email, first_name=first_name, last_name=last_name, profile = profile)
		self.assertEqual(str(user), user.get_full_name())

	def test_user_model_meta_options(self):
		self.assertEqual(User.USERNAME_FIELD, 'email')
		self.assertEqual(User._meta.ordering, ['-date_joined'])

	def test_user_model_function_get_full_name(self):
		"""Check function get_full_name for output"""
		first_name = 'fname'
		last_name = 'lname'
		email = 'email@email.email'
		profile = Profile(name="Onsite", codename="OS")
		user = User(email=email, first_name=first_name, last_name=last_name, profile = profile)
		self.assertEqual(user.get_full_name(), (first_name + ' ' + last_name).strip())
	
	def test_user_model_function_get_short_name(self):
		"""Check function get_short_name for output"""
		first_name = 'fname'
		last_name = 'lname'
		email = 'email@email.email'
		profile = Profile(name="Onsite", codename="OS")
		user = User(email=email, first_name=first_name, last_name=last_name, profile = profile)
		self.assertEqual(user.get_short_name(), first_name)
	
	# def test_user_model_get_remote_img(self):
			# # Defining a user
			# first_name = 'fname'
			# last_name = 'lname'
			# email = 'email@email.email'
			# profile = Profile(name="Onsite", codename="OS")
			# profile.save()
			# user = User(email=email, first_name=first_name, last_name=last_name, profile = profile)
			# user.save()

			# # Null Value
			# url1 = ""
			
			# # Non url entry
			# url2 = "somethingrandom"
			
			# # Url entry with an actual image
			# url3 = "https://spotaxis.com/static/img/logo/logo.png"
			
			# # Url entry that is not an image
			# url4 = "https://spotaxis.com/static/css/style.css"
			
			# # Checks
			# self.assertFalse(user.get_remote_image(url1))
			# self.assertFalse(user.get_remote_image(url2))
			# self.assertTrue(user.get_remote_image(url3))
			# self.assertFalse(user.get_remote_image(url4))

	def test_user_model_property_username_returns_email(self):
		"""Check property usernameto return email instead of field username"""
		profile = Profile(name="Onsite", codename="OS")
		user = User(email='email@email.email', first_name='fname', last_name='lname', profile = profile, username="a")
		self.assertEqual(user.username, user.email)

## Testing User Manager
class UserManagerTest(TestCase):
	"""
	"""

	def test_user_model_manager_create_user_subfunction(self):
		with self.assertRaises(ValueError) as er:
			User.objects.create_user(username="", email="",password="")
		self.assertEqual(str(er.exception), "The given email must be set")

	def test_user_model_manager_create_superuser(self):
		with self.assertRaises(ValueError) as er:
			User.objects.create_superuser(username="", email="email1@email.email", password="pass", is_staff = False)
		self.assertEqual(str(er.exception), "Superuser must have Staff Status.")
		with self.assertRaises(ValueError) as er:
			User.objects.create_superuser(username="", email="email2@email.email", password="pass", is_staff = True, is_superuser=False)
		self.assertEqual(str(er.exception), "Superuser must have Superuser Status.")
		try:
			User.objects.create_superuser(username="", email="email3@email.email", password="pass", is_staff = True, is_superuser=True)
		except:
			self.assertTrue(False)
		try:
			User.objects.create_superuser(username="", email="email4@email.email", password="pass")
		except:
			self.assertTrue(False)