import sys
import os

# This forces the project root into Python's search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from src.process.deduplicator import remove_duplicates
    print("✅ Import Successful!")
except ImportError as e:
    print(f"❌ Import Failed: {e}")
    sys.exit(1)

# ... (rest of your test code)


from src.process.deduplicator import remove_duplicates

def test_logic():
    # Simulated articles with near-duplicate titles
    articles = [
        {
            "title": "Vivek Ramaswamy wins Republican nomination for Ohio governor", 
            "content": "Short summary of the win.", 
            "source": "BBC"
        },
        {
            "title": "Ramaswamy Wins Republican Primary in Ohio Governor Race", 
            "content": "A much longer and more detailed report about the Ohio primary election results...", 
            "source": "Reuters"
        },
        {
            "title": "Unrelated news about a cat in a tree", 
            "content": "Meow.", 
            "source": "Local"
        }
    ]

    print(f"Total articles before: {len(articles)}")
    cleaned = remove_duplicates(articles)
    print(f"Total articles after: {len(cleaned)}")

    for i, a in enumerate(cleaned):
        print(f"Kept [{i}]: {a['title']} (Length: {len(a['content'])})")

    # Verification Logic
    assert len(cleaned) == 2, "Should have removed one duplicate"
    assert "Reuters" in cleaned[0]["source"] or "Reuters" in cleaned[1]["source"], "Should keep the longer content"
    print("\n✅ Deduplication Logic Passed!")

if __name__ == "__main__":
    test_logic()