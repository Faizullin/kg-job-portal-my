from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .test_base import JobPortalAPITestCase
from chat.models import ChatRoom, ChatMessage, ChatParticipant
from orders.models import Order


class TestChatSystem(JobPortalAPITestCase):
    """
    Test chat system functionality.
    These tests mimic the chat features a mobile app would use.
    """
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
    
    def test_chat_room_creation(self):
        """Test creating a new chat room."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:create-room')
        
        chat_data = {
            'name': 'Test Chat Room',
            'room_type': 'order',
            'order': 1  # Use test order from fixtures
        }
        
        response = self.client.post(url, chat_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['name'], 'Test Chat Room')
        
        # Verify chat room was created
        chat_room = ChatRoom.objects.get(id=response.data['id'])
        self.assertEqual(chat_room.name, 'Test Chat Room')
        self.assertEqual(chat_room.room_type, 'order')
    
    def test_chat_room_access_control(self):
        """Test that only participants can access chat rooms."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        # Try to access existing chat room
        url = reverse('chat:room-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Try to access as non-participant
        self.authenticate_user(self.test_admin)
        response = self.client.get(url)
        
        # Should be denied access
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_chat_room_listing(self):
        """Test listing user's chat rooms."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:rooms')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should see the test chat room
        rooms = response.data['results']
        room_names = [room['name'] for room in rooms]
        self.assertIn('Web Development Project Chat', room_names)
    
    def test_chat_room_filtering(self):
        """Test filtering chat rooms by type."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:rooms')
        
        # Filter by order type
        response = self.client.get(url, {'room_type': 'order'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        rooms = response.data['results']
        for room in rooms:
            self.assertEqual(room['room_type'], 'order')
    
    def test_chat_room_search(self):
        """Test searching chat rooms."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:rooms')
        
        # Search by name
        response = self.client.get(url, {'search': 'Web Development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        rooms = response.data['results']
        for room in rooms:
            self.assertIn('Web Development', room['name'])
    
    def test_chat_room_ordering(self):
        """Test ordering chat rooms."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:rooms')
        
        # Order by last message
        response = self.client.get(url, {'ordering': '-last_message'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have last_message field
        rooms = response.data['results']
        if rooms:
            self.assertIn('last_message', rooms[0])
    
    def test_chat_room_participants(self):
        """Test chat room participant management."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('participants', response.data)
        
        # Check participants
        participants = response.data['participants']
        participant_usernames = [p['user']['username'] for p in participants]
        
        self.assertIn('testclient', participant_usernames)
        self.assertIn('testprovider', participant_usernames)
    
    def test_chat_message_sending(self):
        """Test sending messages in chat room."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:send-message')
        
        message_data = {
            'chat_room': 1,
            'content': 'Hello, this is a test message!',
            'message_type': 'text'
        }
        
        response = self.client.post(url, message_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello, this is a test message!')
        
        # Verify message was saved
        message = ChatMessage.objects.get(id=response.data['id'])
        self.assertEqual(message.content, 'Hello, this is a test message!')
        self.assertEqual(message.sender, self.test_client)
    
    def test_chat_message_validation(self):
        """Test message validation."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:send-message')
        
        # Test empty message
        invalid_data = {
            'chat_room': 1,
            'content': '',
            'message_type': 'text'
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid message type
        invalid_data = {
            'chat_room': 1,
            'content': 'Test message',
            'message_type': 'invalid_type'
        }
        
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_chat_message_listing(self):
        """Test listing messages in chat room."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-messages', kwargs={'room_id': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should see existing messages
        messages = response.data['results']
        self.assertGreater(len(messages), 0)
        
        # Check message structure
        if messages:
            message = messages[0]
            self.assertIn('content', message)
            self.assertIn('sender', message)
            self.assertIn('created_at', message)
    
    def test_chat_message_pagination(self):
        """Test message pagination."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-messages', kwargs={'room_id': 1})
        
        # Test pagination
        response = self.client.get(url, {'page': 1, 'page_size': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pagination', response.data)
        
        pagination = response.data['pagination']
        self.assertEqual(pagination['page'], 1)
        self.assertEqual(pagination['page_size'], 5)
    
    def test_chat_message_ordering(self):
        """Test message ordering."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-messages', kwargs={'room_id': 1})
        
        # Order by creation time (newest first)
        response = self.client.get(url, {'ordering': '-created_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        messages = response.data['results']
        if len(messages) > 1:
            # Check that messages are ordered by creation time
            first_time = messages[0]['created_at']
            second_time = messages[1]['created_at']
            self.assertGreaterEqual(first_time, second_time)
    
    def test_chat_message_search(self):
        """Test searching messages."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-messages', kwargs={'room_id': 1})
        
        # Search for specific content
        response = self.client.get(url, {'search': 'Hello'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        messages = response.data['results']
        for message in messages:
            self.assertIn('Hello', message['content'])
    
    def test_chat_message_types(self):
        """Test different message types."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:send-message')
        
        # Test text message
        text_data = {
            'chat_room': 1,
            'content': 'Text message',
            'message_type': 'text'
        }
        
        response = self.client.post(url, text_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_type'], 'text')
        
        # Test system message
        system_data = {
            'chat_room': 1,
            'content': 'System notification',
            'message_type': 'system'
        }
        
        response = self.client.post(url, system_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_type'], 'system')
    
    def test_chat_message_read_status(self):
        """Test message read status functionality."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        # Send a message
        send_url = reverse('chat:send-message')
        message_data = {
            'chat_room': 1,
            'content': 'Test message for read status',
            'message_type': 'text'
        }
        
        response = self.client.post(send_url, message_data)
        message_id = response.data['id']
        
        # Mark message as read
        read_url = reverse('chat:mark-read', kwargs={'message_id': message_id})
        response = self.client.post(read_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify message is marked as read
        message = ChatMessage.objects.get(id=message_id)
        self.assertTrue(message.is_read)
    
    def test_chat_room_notifications(self):
        """Test chat room notification functionality."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-notifications', kwargs={'room_id': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return notification data
        self.assertIn('unread_count', response.data)
        self.assertIn('last_activity', response.data)
    
    def test_chat_room_archiving(self):
        """Test chat room archiving functionality."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:archive-room', kwargs={'pk': 1})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify room is archived
        chat_room = ChatRoom.objects.get(id=1)
        self.assertTrue(chat_room.is_archived)
    
    def test_chat_room_restoration(self):
        """Test chat room restoration functionality."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        # First archive the room
        archive_url = reverse('chat:archive-room', kwargs={'pk': 1})
        self.client.post(archive_url)
        
        # Then restore it
        restore_url = reverse('chat:restore-room', kwargs={'pk': 1})
        response = self.client.post(restore_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify room is restored
        chat_room = ChatRoom.objects.get(id=1)
        self.assertFalse(chat_room.is_archived)
    
    def test_chat_participant_management(self):
        """Test adding and removing chat participants."""
        # Authenticate as admin
        self.authenticate_user(self.test_admin)
        
        url = reverse('chat:add-participant')
        
        participant_data = {
            'chat_room': 1,
            'user': self.test_admin.id,
            'role': 'member'
        }
        
        response = self.client.post(url, participant_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify participant was added
        participant = ChatParticipant.objects.get(
            chat_room_id=1,
            user=self.test_admin
        )
        self.assertEqual(participant.role, 'member')
    
    def test_chat_participant_removal(self):
        """Test removing chat participants."""
        # Authenticate as admin
        self.authenticate_user(self.test_admin)
        
        # First add a participant
        add_url = reverse('chat:add-participant')
        participant_data = {
            'chat_room': 1,
            'user': self.test_admin.id,
            'role': 'member'
        }
        self.client.post(add_url, participant_data)
        
        # Then remove them
        remove_url = reverse('chat:remove-participant', kwargs={'room_id': 1, 'user_id': self.test_admin.id})
        response = self.client.post(remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify participant was removed
        participant_exists = ChatParticipant.objects.filter(
            chat_room_id=1,
            user=self.test_admin
        ).exists()
        self.assertFalse(participant_exists)
    
    def test_chat_room_permissions(self):
        """Test chat room permission system."""
        # Authenticate as regular user
        self.authenticate_user(self.test_client)
        
        # Try to add participant (should fail - not admin)
        url = reverse('chat:add-participant')
        participant_data = {
            'chat_room': 1,
            'user': self.test_admin.id,
            'role': 'member'
        }
        
        response = self.client.post(url, participant_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to delete chat room (should fail - not admin)
        delete_url = reverse('chat:delete-room', kwargs={'pk': 1})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_chat_message_editing(self):
        """Test editing chat messages."""
        # Authenticate as message sender
        self.authenticate_user(self.test_client)
        
        # Send a message first
        send_url = reverse('chat:send-message')
        message_data = {
            'chat_room': 1,
            'content': 'Original message content',
            'message_type': 'text'
        }
        
        response = self.client.post(send_url, message_data)
        message_id = response.data['id']
        
        # Edit the message
        edit_url = reverse('chat:edit-message', kwargs={'pk': message_id})
        edit_data = {
            'content': 'Edited message content'
        }
        
        response = self.client.patch(edit_url, edit_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Edited message content')
        
        # Verify message was updated
        message = ChatMessage.objects.get(id=message_id)
        self.assertEqual(message.content, 'Edited message content')
    
    def test_chat_message_deletion(self):
        """Test deleting chat messages."""
        # Authenticate as message sender
        self.authenticate_user(self.test_client)
        
        # Send a message first
        send_url = reverse('chat:send-message')
        message_data = {
            'chat_room': 1,
            'content': 'Message to delete',
            'message_type': 'text'
        }
        
        response = self.client.post(send_url, message_data)
        message_id = response.data['id']
        
        # Delete the message
        delete_url = reverse('chat:delete-message', kwargs={'pk': message_id})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify message was deleted
        message_exists = ChatMessage.objects.filter(id=message_id).exists()
        self.assertFalse(message_exists)
    
    def test_chat_room_search_functionality(self):
        """Test searching within chat rooms."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:search-messages')
        
        # Search for messages containing specific text
        search_params = {
            'q': 'Hello',
            'room_id': 1
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should find messages containing "Hello"
        messages = response.data['results']
        for message in messages:
            self.assertIn('Hello', message['content'])
    
    def test_chat_room_statistics(self):
        """Test chat room statistics functionality."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        url = reverse('chat:room-stats', kwargs={'room_id': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return statistics
        self.assertIn('total_messages', response.data)
        self.assertIn('participant_count', response.data)
        self.assertIn('last_activity', response.data)
    
    def test_chat_system_performance(self):
        """Test chat system performance."""
        import time
        
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        # Test message listing performance
        url = reverse('chat:room-messages', kwargs={'room_id': 1})
        
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
        
        # Test room listing performance
        rooms_url = reverse('chat:rooms')
        
        start_time = time.time()
        response = self.client.get(rooms_url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
    
    def test_chat_system_mobile_optimization(self):
        """Test that chat system is mobile-optimized."""
        # Authenticate as client
        self.authenticate_user(self.test_client)
        
        # Test room listing with mobile-friendly response
        url = reverse('chat:rooms')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure for mobile optimization
        rooms = response.data['results']
        if rooms:
            room = rooms[0]
            essential_fields = ['id', 'name', 'room_type', 'last_message', 'participant_count']
            
            for field in essential_fields:
                self.assertIn(field, room)
            
            # Check that response is not too verbose
            response_size = len(str(response.content))
            self.assertLess(response_size, 15000)  # Response should be reasonably sized
        
        # Test message listing with mobile-friendly response
        messages_url = reverse('chat:room-messages', kwargs={'room_id': 1})
        response = self.client.get(messages_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        messages = response.data['results']
        if messages:
            message = messages[0]
            essential_fields = ['id', 'content', 'sender', 'created_at', 'message_type']
            
            for field in essential_fields:
                self.assertIn(field, message)

