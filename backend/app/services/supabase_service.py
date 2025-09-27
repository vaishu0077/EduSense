"""
Supabase service for database operations, authentication, and storage
"""

from supabase import create_client, Client
from typing import Dict, List, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for Supabase operations"""
    
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be configured")
        
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.service_client: Optional[Client] = None
        
        if settings.SUPABASE_SERVICE_KEY:
            self.service_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    # Authentication methods
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sign up a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data
                }
            })
            return response
        except Exception as e:
            logger.error(f"Error signing up user: {str(e)}")
            raise Exception(f"Failed to sign up user: {str(e)}")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            logger.error(f"Error signing in user: {str(e)}")
            raise Exception(f"Failed to sign in user: {str(e)}")
    
    async def sign_out(self) -> None:
        """Sign out current user"""
        try:
            self.client.auth.sign_out()
        except Exception as e:
            logger.error(f"Error signing out user: {str(e)}")
            raise Exception(f"Failed to sign out user: {str(e)}")
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        try:
            user = self.client.auth.get_user()
            return user.user if user.user else None
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None
    
    # Database operations
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table"""
        try:
            response = self.client.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error inserting into {table}: {str(e)}")
            raise Exception(f"Failed to insert into {table}: {str(e)}")
    
    async def select(self, table: str, columns: str = "*", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Select data from a table"""
        try:
            query = self.client.table(table).select(columns)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error selecting from {table}: {str(e)}")
            raise Exception(f"Failed to select from {table}: {str(e)}")
    
    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update data in a table"""
        try:
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error updating {table}: {str(e)}")
            raise Exception(f"Failed to update {table}: {str(e)}")
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Delete data from a table"""
        try:
            query = self.client.table(table)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.delete().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error deleting from {table}: {str(e)}")
            raise Exception(f"Failed to delete from {table}: {str(e)}")
    
    # Storage operations
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload file to Supabase storage"""
        try:
            response = self.client.storage.from_(bucket).upload(file_path, file_data, {
                "content-type": content_type
            })
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def delete_file(self, bucket: str, file_path: str) -> None:
        """Delete file from Supabase storage"""
        try:
            self.client.storage.from_(bucket).remove([file_path])
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    async def get_file_url(self, bucket: str, file_path: str) -> str:
        """Get public URL for a file"""
        try:
            return self.client.storage.from_(bucket).get_public_url(file_path)
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            raise Exception(f"Failed to get file URL: {str(e)}")
    
    # Real-time subscriptions
    async def subscribe_to_changes(self, table: str, callback, filters: Optional[Dict[str, Any]] = None):
        """Subscribe to real-time changes in a table"""
        try:
            subscription = self.client.table(table).on('*', callback).subscribe()
            return subscription
        except Exception as e:
            logger.error(f"Error subscribing to {table}: {str(e)}")
            raise Exception(f"Failed to subscribe to {table}: {str(e)}")

# Initialize Supabase service
supabase_service = SupabaseService()
