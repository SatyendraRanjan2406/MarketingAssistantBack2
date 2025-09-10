"""
Django management command to set up the RAG system
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

from google_ads_new.document_scraper import scrape_google_ads_docs
from google_ads_new.vector_store import setup_vector_store
from google_ads_new.rag_client import initialize_rag_client

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up the RAG system by scraping Google Ads documentation and creating embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Recreate the vector store collection (deletes existing data)',
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Size of text chunks (default: 1000)',
        )
        parser.add_argument(
            '--chunk-overlap',
            type=int,
            default=200,
            help='Overlap between chunks (default: 200)',
        )
        parser.add_argument(
            '--collection-name',
            type=str,
            default='google_ads_docs',
            help='Name of the vector store collection (default: google_ads_docs)',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting RAG system setup...')
            )
            
            # Check required environment variables
            if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
                raise CommandError(
                    'OPENAI_API_KEY is not set. Please set it in your environment or Django settings.'
                )
            
            # Scrape documents
            self.stdout.write('Scraping Google Ads documentation...')
            documents = scrape_google_ads_docs()
            
            if not documents:
                raise CommandError('No documents were scraped. Please check your internet connection and try again.')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully scraped {len(documents)} document chunks')
            )
            
            # Setup vector store
            self.stdout.write('Setting up vector store...')
            vector_store = setup_vector_store(
                documents, 
                recreate=options['recreate']
            )
            
            self.stdout.write(
                self.style.SUCCESS('Vector store setup completed')
            )
            
            # Initialize RAG client
            self.stdout.write('Initializing RAG client...')
            rag_client = initialize_rag_client(
                collection_name=options['collection_name']
            )
            
            # Get collection stats
            stats = rag_client.get_collection_stats()
            self.stdout.write(
                self.style.SUCCESS(f'RAG system setup completed successfully!')
            )
            self.stdout.write(f'Collection: {stats.get("collection_name", "N/A")}')
            self.stdout.write(f'Total points: {stats.get("total_points", "N/A")}')
            self.stdout.write(f'Indexed vectors: {stats.get("indexed_vectors", "N/A")}')
            
            self.stdout.write(
                self.style.SUCCESS('\nRAG system is ready! You can now query it using the API endpoints.')
            )
            
        except Exception as e:
            logger.error(f"Error setting up RAG system: {e}")
            raise CommandError(f'Failed to set up RAG system: {e}')
