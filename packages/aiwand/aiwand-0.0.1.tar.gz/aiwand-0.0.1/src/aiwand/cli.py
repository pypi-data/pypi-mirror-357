"""
Command Line Interface for AIWand
"""

import argparse
import sys
from typing import Optional
from .core import summarize, chat, generate_text
from .config import configure_api_key


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AIWand - AI toolkit for text processing")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize text')
    summarize_parser.add_argument('text', help='Text to summarize')
    summarize_parser.add_argument('--style', choices=['concise', 'detailed', 'bullet-points'], 
                                 default='concise', help='Summary style')
    summarize_parser.add_argument('--max-length', type=int, help='Maximum length in words')
    summarize_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Chat with AI')
    chat_parser.add_argument('message', help='Message to send')
    chat_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    chat_parser.add_argument('--temperature', type=float, default=0.7, help='Response creativity')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate text from prompt')
    generate_parser.add_argument('prompt', help='Prompt for text generation')
    generate_parser.add_argument('--max-tokens', type=int, default=500, help='Maximum tokens to generate')
    generate_parser.add_argument('--temperature', type=float, default=0.7, help='Response creativity')
    generate_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure API key')
    config_parser.add_argument('api_key', help='OpenAI API key')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'summarize':
            result = summarize(
                text=args.text,
                max_length=args.max_length,
                style=args.style,
                model=args.model
            )
            print(result)
            
        elif args.command == 'chat':
            result = chat(
                message=args.message,
                model=args.model,
                temperature=args.temperature
            )
            print(result)
            
        elif args.command == 'generate':
            result = generate_text(
                prompt=args.prompt,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                model=args.model
            )
            print(result)
            
        elif args.command == 'config':
            configure_api_key(args.api_key)
            print("API key configured successfully!")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 