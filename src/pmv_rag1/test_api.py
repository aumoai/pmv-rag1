#!/usr/bin/env python3
"""
Simple test script for the RAG Chatbot API
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_config():
    """Test configuration loading"""
    try:
        from pmv_rag1.config import validate_config

        validate_config()
        logger.info("✅ Configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False


async def test_gemini_client():
    """Test Gemini client initialization"""
    try:
        from pmv_rag1.services.gemini_client import GeminiClient

        GeminiClient()
        logger.info("✅ Gemini client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Gemini client initialization failed: {e}")
        return False


async def test_vector_store():
    """Test vector store initialization"""
    try:
        from pmv_rag1.retriever.vectorstore import VectorStore

        VectorStore()
        logger.info("✅ Vector store initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Vector store initialization failed: {e}")
        return False


async def test_file_parser():
    """Test file parser"""
    try:
        from pmv_rag1.processors.file_parser import FileParser

        parser = FileParser()
        supported_extensions = parser.get_supported_extensions()  # pyright: ignore[reportUnknownMemberType]
        logger.info(f"✅ File parser initialized. Supported extensions: {supported_extensions}")
        return True
    except Exception as e:
        logger.error(f"❌ File parser initialization failed: {e}")
        return False


async def test_speech_to_text():
    """Test speech-to-text processor"""
    try:
        from pmv_rag1.processors.speech_to_text import SpeechToText

        stt = SpeechToText()
        model_info = stt.get_model_info()
        logger.info(f"✅ Speech-to-text initialized. Model info: {model_info}")
        return True
    except Exception as e:
        logger.error(f"❌ Speech-to-text initialization failed: {e}")
        return False


async def test_orchestrator():
    """Test orchestrator initialization"""
    try:
        from pmv_rag1.services.orchestrator import Orchestrator

        Orchestrator()
        logger.info("✅ Orchestrator initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Orchestrator initialization failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting API tests...")

    tests = [
        ("Configuration", test_config),
        ("Gemini Client", test_gemini_client),
        ("Vector Store", test_vector_store),
        ("File Parser", test_file_parser),
        ("Speech-to-Text", test_speech_to_text),
        ("Orchestrator", test_orchestrator),
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False

    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! API is ready to use.")
    else:
        logger.error("⚠️  Some tests failed. Please check the configuration and dependencies.")

    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_tests())
