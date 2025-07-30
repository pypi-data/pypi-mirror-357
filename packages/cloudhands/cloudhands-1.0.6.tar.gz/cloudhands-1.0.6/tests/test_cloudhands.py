import os
from src.cloudhands import CloudHands
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize CloudHands
    api_key = os.getenv("API_KEY")
    ch = CloudHands(
        api_key=api_key,
    )
    
    print("Test get userid by username")
    user_id = ch.get_user_id("connor")
    print("User ID:", user_id)

    print("Test get posts by user id")
    posts = ch.get_posts(user_id)
    print("Posts:", posts)
    print("sample first post:", posts[0].__dict__)

    print("Test like post")
    like_result = ch.like_post(posts[0].postId)
    print("Like result:", like_result)
    
    # Prompt the user to enter a title for the test post
    title = input("Enter a title to create a test post, or hit enter to skip: ").strip()
    if title:
        try:
            response = ch.text_post(title=title, content="This post was created using the python SDK.")
            print(f"Test post created successfully: {response}")
        except Exception as e:
            print(f"Failed to create test post: {e}")
    else:
        print("Test post creation skipped.")
    
    # Test uploading the tree.jpg file in the current directory
    file_path = "./tests/tree.jpg"
    try:
        response = ch.upload_image(image_path=file_path)
        print(f"File uploaded successfully: {response}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Failed to upload file: {e}")

    # Test image post
    # Prompt the user to enter a title for the test post
    title = input("Enter a title to create a test post, or hit enter to skip: ").strip()
    if title:
        try:
            response = ch.image_post(title=title, content="This post was created using the python SDK.", image_path=file_path)
            print(f"Test post created successfully: {response}")
        except Exception as e:
            print(f"Failed to create test post: {e}")
    else:
        print("Test post creation skipped.")

if __name__ == "__main__":
    main()

