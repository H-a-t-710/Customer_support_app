import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for interacting with Google's Gemini language model.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM service.
        
        Args:
            api_key (str, optional): Google Gemini API key
            model (str, optional): Gemini model name
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(self.model_name)
        
    def generate_response(self, query: str, context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response using the LLM based on query and context.
        
        Args:
            query (str): User query
            context (List[Dict[str, Any]], optional): List of context documents
            
        Returns:
            Dict[str, Any]: Response text and source citations
        """
        try:
            if not context or len(context) == 0:
                # No context available, return "I don't know" response
                return self._generate_dont_know_response(query)
            
            # Prepare content with context
            formatted_context = self._format_context(context)
            
            # Create a prompt that instructs the model to use the context
            prompt = self._create_rag_prompt(query, formatted_context)
            
            # Set generation config for better responses
            generation_config = {
                "temperature": 0.3,  # Lower temperature for more factual responses
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2500,
            }
            
            # Generate response with improved parameters
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Process response to extract citations
            result = self._process_response(response.text, context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """
        Format context documents for inclusion in the prompt.
        
        Args:
            context (List[Dict[str, Any]]): List of context documents
            
        Returns:
            str: Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(context):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "")
            source_type = metadata.get("source_type", "")
            
            # Format source citation with more details
            if source_type == "web" or source_type == "web_faq":
                source_citation = f"[Web Document {i+1}: {source}]"
            else:
                source_name = source.replace("_", " ").replace(".pdf", "").replace(".docx", "")
                if page:
                    source_citation = f"[Document {i+1}: {source_name} (Page {page})]"
                else:
                    source_citation = f"[Document {i+1}: {source_name}]"
            
            # Add to context parts
            context_parts.append(f"{source_citation}\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """
        Create a RAG prompt for the LLM.
        
        Args:
            query (str): User query
            context (str): Formatted context string
            
        Returns:
            str: Complete prompt for the LLM
        """
        return f"""You are an AI assistant specialized in answering customer support questions about:
1. Insurance plans and policies based on the America's Choice documents
2. Angel One's investment, stock market, and brokerage services web contents

Your task is to provide accurate, helpful responses based ONLY on the information in the provided context documents and web contents.

IMPORTANT INSTRUCTIONS:
1. Base your answers EXCLUSIVELY on the information in the context provided below.
2. If the information needed to answer the question is not present in the context, respond with "I Don't know."
3. DO NOT make up or infer information that is not explicitly stated in the context.
4. If multiple documents contain relevant information, cite all of them.
5. Be concise but thorough in your answers and do not include documets or content you refering to.
6. Format your response in a clear, readable way. Do NOT use bullet points, asterisks (*), or dashes (-) in your answer. Present the information in plain sentences or a numbered list if needed.
7. For financial or insurance-specific terms, provide brief explanations if available in the context.
8. If answering questions about Angel One services, cite the specific web document sources.
9. If answering insurance questions, specify which insurance document you're using.
10. If user do not have exact question but close to context then help with relavant context information.

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:"""
    
    def _process_response(self, response_text: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process the response to extract citations and ensure quality.
        
        Args:
            response_text (str): Raw response text from the LLM
            context (List[Dict[str, Any]]): List of context documents
            
        Returns:
            Dict[str, Any]: Processed response with text and sources
        """
        # Extract sources from the response
        sources = []
        
        # Check for document references in the response
        for i, doc in enumerate(context):
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "")
            similarity = doc.get("similarity", 0)
            source_type = metadata.get("source_type", "")
            
            # Format source name for display
            if source_type == "web" or source_type == "web_faq":
                source_name = source
                doc_marker = f"Web Document {i+1}"
            else:
                source_name = source.replace("_", " ").replace(".pdf", "").replace(".docx", "")
                doc_marker = f"Document {i+1}"
            
            # Check if this document is cited (improved detection)
            if doc_marker in response_text:
                source_info = {
                    "content": doc.get("content", ""),
                    "metadata": {
                        "source": source_name,
                        "page": page if page else None,
                        "source_type": source_type
                    },
                    "similarity": similarity
                }
                if not any(s["metadata"]["source"] == source_name and s["metadata"]["page"] == page for s in sources):
                    sources.append(source_info)
        
        # If no sources were explicitly cited but we used context, include the top sources
        if not sources and context:
            # Sort by similarity and take top 2
            sorted_context = sorted(context, key=lambda x: x.get("similarity", 0), reverse=True)
            for doc in sorted_context[:2]:
                metadata = doc.get("metadata", {})
                source = metadata.get("source", "Unknown")
                page = metadata.get("page", "")
                similarity = doc.get("similarity", 0)
                source_type = metadata.get("source_type", "")
                
                # Format source name for display
                if source_type == "web" or source_type == "web_faq":
                    source_name = source
                else:
                    source_name = source.replace("_", " ").replace(".pdf", "").replace(".docx", "")
                
                source_info = {
                    "content": doc.get("content", ""),
                    "metadata": {
                        "source": source_name,
                        "page": page if page else None,
                        "source_type": source_type
                    },
                    "similarity": similarity
                }
                sources.append(source_info)
        
        return {
            "text": response_text,
            "sources": sources
        }
    
    def _generate_dont_know_response(self, query: str) -> Dict[str, Any]:
        """
        Generate an "I don't know" response.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: Response indicating lack of knowledge
        """
        return {
            "text": "I Don't Know.",
            "sources": []
        }