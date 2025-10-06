"""
Quick test script to verify AI Service v2.0 is working
"""

import requests
import sys
from PIL import Image, ImageDraw, ImageFont
import io

def test_health():
    """Test if service is running"""
    print("🔍 Testing service health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Service is running")
            print(f"   Status: {health['status']}")
            print(f"   Components:")
            for component, status in health['components'].items():
                icon = "✅" if "healthy" in status else "⚠️"
                print(f"     {icon} {component}: {status}")
            return True
        else:
            print(f"❌ Service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Is it running?")
        print("   Start with: python main_v2.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def create_test_document():
    """Create a simple test document image"""
    print("\n📄 Creating test document...")
    
    # Create image with text
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add sample FRA form text
    text = """
    FOREST RIGHTS ACT - FORM A
    Individual Forest Rights Claim
    
    Name of Claimant: Ram Kumar
    Father's Name: Shyam Lal
    Village: Bastar Village
    District: Khargone
    State: Madhya Pradesh
    
    Land Area: 2.5 hectares
    Survey Number: 123/45
    
    Application Date: 15/09/2024
    """
    
    try:
        # Try to use a font
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Draw text
    y = 50
    for line in text.strip().split('\n'):
        draw.text((50, y), line.strip(), fill='black', font=font)
        y += 30
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print("✅ Test document created")
    return img_bytes


def test_document_processing():
    """Test document processing with ML NER"""
    print("\n🧠 Testing ML-based document processing...")
    
    try:
        # Create test image
        test_image = create_test_document()
        
        # Send to API
        files = {'file': ('test_document.png', test_image, 'image/png')}
        data = {
            'language': 'auto',
            'use_ml_ner': 'true'
        }
        
        print("   Sending document to API...")
        response = requests.post(
            "http://localhost:8000/api/process-document",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document processed successfully!")
            print(f"\n📊 Results:")
            print(f"   Processing Mode: {result.get('processing_mode')}")
            print(f"   Form Type: {result.get('form_type')} (confidence: {result.get('form_confidence', 0):.2f})")
            print(f"   OCR Confidence: {result.get('ocr_confidence', 0):.2f}")
            print(f"   Overall Confidence: {result.get('overall_confidence', 0):.2f}")
            
            print(f"\n📝 Extracted Entities:")
            entities = result.get('entities', {})
            confidence_scores = result.get('confidence_scores', {})
            
            if entities:
                for field, value in entities.items():
                    confidence = confidence_scores.get(field, 0)
                    print(f"     {field}: {value} (confidence: {confidence:.2f})")
            else:
                print("     No entities extracted (may need better OCR or different image)")
            
            return True
        else:
            print(f"❌ Processing failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processing():
    """Test batch processing API"""
    print("\n📦 Testing batch processing...")
    
    try:
        # Create batch job with mock documents
        batch_data = {
            "documents": [
                {"document_id": "test_doc_1", "file_path": "test1.jpg"},
                {"document_id": "test_doc_2", "file_path": "test2.jpg"},
                {"document_id": "test_doc_3", "file_path": "test3.jpg"},
            ],
            "priority": 5,
            "metadata": {"test": True}
        }
        
        print("   Creating batch job...")
        response = requests.post(
            "http://localhost:8000/api/batch/create",
            json=batch_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            batch_id = result['batch_id']
            print(f"✅ Batch job created: {batch_id}")
            print(f"   Status: {result['status']}")
            
            # Wait a moment for processing
            import time
            time.sleep(2)
            
            # Check status
            print(f"\n   Checking batch status...")
            status_response = requests.get(
                f"http://localhost:8000/api/batch/status/{batch_id}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"✅ Batch status retrieved:")
                print(f"     Status: {status['status']}")
                print(f"     Progress: {status['progress']}%")
                print(f"     Processed: {status['processed']}/{status['total_documents']}")
                print(f"     Successful: {status['successful']}")
                print(f"     Failed: {status['failed']}")
                return True
            else:
                print(f"⚠️ Could not retrieve batch status")
                return False
        else:
            print(f"❌ Batch creation failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during batch test: {str(e)}")
        return False


def test_stats():
    """Test statistics endpoint"""
    print("\n📊 Testing statistics endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistics retrieved:")
            print(f"   Total Jobs: {stats.get('total_jobs', 0)}")
            print(f"   Documents Processed: {stats.get('total_documents_processed', 0)}")
            print(f"   ML Models:")
            for model, status in stats.get('ml_models', {}).items():
                print(f"     - {model}: {status}")
            return True
        else:
            print(f"❌ Stats endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("FRA Atlas AI Service v2.0 - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Document Processing", test_document_processing),
        ("Batch Processing", test_batch_processing),
        ("Statistics", test_stats),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Service is working perfectly!")
        print("\n📚 Next steps:")
        print("   1. Try with your own FRA documents")
        print("   2. Check API docs: http://localhost:8000/docs")
        print("   3. Read UPGRADE_SUMMARY.md for usage examples")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\n💡 Common issues:")
        print("   - Service not running: python main_v2.py")
        print("   - Missing dependencies: pip install -r requirements_ml.txt")
        print("   - SpaCy models: python -m spacy download en_core_web_sm")
        return 1


if __name__ == "__main__":
    sys.exit(main())
