from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Resource
from .forms import ResourceForm


User = get_user_model()


@override_settings(
	STORAGES={
		"default": {
			"BACKEND": "django.core.files.storage.FileSystemStorage",
		},
		"staticfiles": {
			"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
		},
	}
)
class ResourceListViewTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="owner",
			password="testpass123",
			email="owner@example.com",
		)
		self.approved = Resource.objects.create(
			title="Approved Resource",
			link="https://example.com/approved",
			description="Approved description",
			username=self.user,
			approved=True,
		)
		self.unapproved = Resource.objects.create(
			title="Unapproved Resource",
			link="https://example.com/unapproved",
			description="Unapproved description",
			username=self.user,
			approved=False,
		)

	def test_list_shows_only_approved(self):
		response = self.client.get(reverse("home"))
		self.assertContains(response, "Approved Resource")
		self.assertNotContains(response, "Unapproved Resource")

	def test_pagination_buttons(self):
		Resource.objects.all().delete()
		for i in range(7):
			Resource.objects.create(
				title=f"Resource {i}",
				link=f"https://example.com/{i}",
				description="Desc",
				username=self.user,
				approved=True,
			)

		response = self.client.get(reverse("home"))
		self.assertContains(response, "Next »")
		self.assertNotContains(response, "« Previous")

		response_page_2 = self.client.get(f"{reverse('home')}?page=2")
		self.assertContains(response_page_2, "« Previous")

	def test_create_requires_login(self):
		response = self.client.post(
			reverse("home"),
			{
				"title": "New Resource",
				"link": "https://example.com/new",
				"description": "New description",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Resource.objects.filter(title="New Resource").count(), 0)

	def test_create_authenticated_creates_unapproved(self):
		self.client.login(username="owner", password="testpass123")
		response = self.client.post(
			reverse("home"),
			{
				"title": "New Resource",
				"link": "https://example.com/new",
				"description": "New description",
			},
		)
		self.assertEqual(response.status_code, 302)
		resource = Resource.objects.get(title="New Resource")
		self.assertFalse(resource.approved)
		self.assertEqual(resource.username, self.user)
		self.assertTrue(resource.slug)

	def test_invalid_url_rejected(self):
		self.client.login(username="owner", password="testpass123")
		response = self.client.post(
			reverse("home"),
			{
				"title": "Bad URL",
				"link": "not-a-url",
				"description": "Desc",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Resource.objects.filter(title="Bad URL").count(), 0)


@override_settings(
	STORAGES={
		"default": {
			"BACKEND": "django.core.files.storage.FileSystemStorage",
		},
		"staticfiles": {
			"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
		},
	}
)
class ResourcePermissionTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(
			username="owner",
			password="testpass123",
			email="owner@example.com",
		)
		self.other = User.objects.create_user(
			username="other",
			password="testpass123",
			email="other@example.com",
		)
		self.resource = Resource.objects.create(
			title="Owner Resource",
			link="https://example.com/owner",
			description="Owner description",
			username=self.owner,
			approved=True,
		)

	def test_owner_can_edit(self):
		self.client.login(username="owner", password="testpass123")
		past = timezone.now() - timezone.timedelta(days=1)
		Resource.objects.filter(pk=self.resource.pk).update(updated_at=past)
		self.resource.refresh_from_db()
		previous_updated_at = self.resource.updated_at
		response = self.client.post(
			reverse("resource_edit", args=[self.resource.slug]),
			{
				"title": "Updated Title",
				"link": "https://example.com/owner",
				"description": "Updated description",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.resource.refresh_from_db()
		self.assertEqual(self.resource.title, "Updated Title")
		self.assertGreater(self.resource.updated_at, previous_updated_at)

	def test_non_owner_cannot_edit(self):
		self.client.login(username="other", password="testpass123")
		response = self.client.post(
			reverse("resource_edit", args=[self.resource.slug]),
			{
				"title": "Hacked Title",
				"link": "https://example.com/owner",
				"description": "Hacked description",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.resource.refresh_from_db()
		self.assertEqual(self.resource.title, "Owner Resource")

	def test_owner_can_delete(self):
		self.client.login(username="owner", password="testpass123")
		response = self.client.post(
			reverse("resource_delete", args=[self.resource.slug])
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Resource.objects.count(), 0)
		list_response = self.client.get(reverse("home"))
		self.assertNotContains(list_response, "Owner Resource")

	def test_non_owner_cannot_delete(self):
		self.client.login(username="other", password="testpass123")
		response = self.client.post(
			reverse("resource_delete", args=[self.resource.slug])
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Resource.objects.count(), 1)


@override_settings(
	STORAGES={
		"default": {
			"BACKEND": "django.core.files.storage.FileSystemStorage",
		},
		"staticfiles": {
			"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
		},
	}
)
class ResourceFormTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="owner",
			password="testpass123",
			email="owner@example.com",
		)
		Resource.objects.create(
			title="Case Test",
			link="https://example.com/case",
			description="Case description",
			username=self.user,
			approved=True,
		)

	def test_title_case_insensitive_unique(self):
		form = ResourceForm(
			data={
				"title": "case test",
				"link": "https://example.com/case-2",
				"description": "Another description",
			}
		)
		self.assertFalse(form.is_valid())
		self.assertIn("title", form.errors)


@override_settings(
	STORAGES={
		"default": {
			"BACKEND": "django.core.files.storage.FileSystemStorage",
		},
		"staticfiles": {
			"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
		},
	}
)
class RegistrationTests(TestCase):
	def test_registration_creates_user_and_redirects(self):
		response = self.client.post(
			reverse("account_signup"),
			{
				"username": "newuser",
				"email": "newuser@example.com",
				"password1": "StrongPass123!",
				"password2": "StrongPass123!",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/")
		home = self.client.get(reverse("home"))
		self.assertTrue(home.wsgi_request.user.is_authenticated)

	def test_duplicate_email_rejected(self):
		User.objects.create_user(
			username="existing",
			email="dup@example.com",
			password="StrongPass123!",
		)
		response = self.client.post(
			reverse("account_signup"),
			{
				"username": "newuser",
				"email": "dup@example.com",
				"password1": "StrongPass123!",
				"password2": "StrongPass123!",
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "email", status_code=200)
