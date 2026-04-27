from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile


class ProfileBlockEndpointsTests(APITestCase):
    def setUp(self):
        self.actor = User.objects.create_user(username='alice', password='secret123')
        self.target = User.objects.create_user(username='bob', password='secret123')

        self.actor_profile = Profile.objects.create(user=self.actor, name='Alice')
        self.target_profile = Profile.objects.create(user=self.target, name='Bob')

        self.client.force_authenticate(user=self.actor)

    def test_block_user_endpoint_adds_target_to_blocked_users(self):
        response = self.client.patch(f'/users/blacklist/add/{self.target.username}/')

        self.actor_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.actor_profile.blocked_users.filter(pk=self.target.pk).exists())

    def test_unblock_user_endpoint_removes_target_from_blocked_users(self):
        self.actor_profile.blocked_users.add(self.target)

        response = self.client.patch(f'/users/blacklist/remove/{self.target.username}/')

        self.actor_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.actor_profile.blocked_users.filter(pk=self.target.pk).exists())

    def test_block_user_endpoint_rejects_self_block(self):
        response = self.client.patch(f'/users/blacklist/add/{self.actor.username}/')

        self.actor_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.actor_profile.blocked_users.filter(pk=self.actor.pk).exists())
