from django.http import JsonResponse, HttpResponse  # Import JsonResponse and HttpResponse
import json
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# Utility functions for loading and saving JSON data
def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


# Sign-up view
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        users = load_json('users.json')
        new_user = {
            "user_name": username,
            "password": password,
            "favorite_tags": [],
            "watched_movies": [],
            "wishlist_movies": [],
            "reviews": []
        }

        users.append(new_user)
        save_json('users.json', users)

        return JsonResponse({"message": "Signup successful, please login."}, status=201)

    return JsonResponse({"error": "Only POST method is allowed"}, status=400)


# Login view
@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)

            users = load_json('users.json')

            user = next((u for u in users if u['user_name'] == username and u['password'] == password), None)

            if user:
                return JsonResponse({"message": "Login successful", "user_name": user['user_name']}, status=200)
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Only POST method is allowed"}, status=400)


# Home view for selecting tags
@csrf_exempt
@csrf_exempt
def home(request, user_name):
    if request.method == 'POST':
        try:
            # Parse the raw JSON data from the request body (tags)
            data = json.loads(request.body.decode('utf-8'))
            selected_tags = data.get('tags', [])

            # Load user and save selected tags
            users = load_json('users.json')
            user = next((u for u in users if u['user_name'] == user_name), None)

            if user:
                user['favorite_tags'] = selected_tags
                save_json('users.json', users)
                
                # Redirect to the suggestions page with the user_name
                return JsonResponse({
                    "message": "Tags saved successfully, redirecting to suggestions",
                    "redirect_url": f"/suggestions/{user_name}/"
                }, status=200)
            else:
                return JsonResponse({"error": "User not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Only POST method is allowed"}, status=400)


@csrf_exempt
def movie_detail(request, movie_id, user_name):
    if request.method == 'GET':
        # Fetch the movie details for the given movie ID
        movies = load_json('movies.json')
        reviews = load_json('reviews.json')

        movie = next((m for m in movies if m['id'] == movie_id), None)
        if not movie:
            return JsonResponse({"error": "Movie not found"}, status=404)

        # Find all reviews for the movie
        movie_reviews = [review for review in reviews if review['movie_id'] == movie_id]

        # Return movie details along with reviews
        return JsonResponse({
            "movie": movie,
            "reviews": movie_reviews
        }, status=200)

    elif request.method == 'POST':
        try:
            # Post a review for the movie
            data = json.loads(request.body.decode('utf-8'))
            comment = data.get('comment', '')

            movies = load_json('movies.json')
            reviews = load_json('reviews.json')
            users = load_json('users.json')

            user = next((u for u in users if u['user_name'] == user_name), None)
            movie = next((m for m in movies if m['id'] == movie_id), None)

            if not user:
                return JsonResponse({"error": "User not found"}, status=404)
            if not movie:
                return JsonResponse({"error": "Movie not found"}, status=404)

            # Add new review
            new_review = {
                "user_name": user_name,
                "movie_id": movie_id,
                "comment": comment
            }
            reviews.append(new_review)
            save_json('reviews.json', reviews)

            # Return success message
            return JsonResponse({"message": "Review added successfully"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Only GET and POST methods are allowed"}, status=400)

# View for showing favorite movies based on selected tags
def favorites(request, user_name):
    movies = load_json('movies.json')
    users = load_json('users.json')

    user = next((u for u in users if u['user_name'] == user_name), None)

    if user:
        favorite_movies = [m for m in movies if any(tag in m['tags'] for tag in user['favorite_tags'])]
        return JsonResponse({"favorite_movies": favorite_movies}, status=200)
    else:
        return JsonResponse({"error": "User not found"}, status=404)


# View for showing details of a movie and posting reviews
@csrf_exempt
def movie_detail(request, movie_id, user_name):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            comment = data.get('comment', '')

            movies = load_json('movies.json')
            reviews = load_json('reviews.json')
            users = load_json('users.json')

            user = next((u for u in users if u['user_name'] == user_name), None)
            movie = next((m for m in movies if m['id'] == movie_id), None)

            if not user:
                return JsonResponse({"error": "User not found"}, status=404)
            if not movie:
                return JsonResponse({"error": "Movie not found"}, status=404)

            new_review = {
                "user_name": user_name,
                "movie_id": movie_id,
                "comment": comment
            }
            reviews.append(new_review)
            save_json('reviews.json', reviews)

            return JsonResponse({"message": "Review added successfully"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Only POST method is allowed"}, status=400)


# View for updating movie status (watched, watching, wishlist)
@csrf_exempt
def update_status(request, movie_id, status, user_name):
    try:
        users = load_json('users.json')
        user = next((u for u in users if u['user_name'] == user_name), None)

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        if status == 'watched' and movie_id not in user['watched_movies']:
            user['watched_movies'].append(movie_id)
        elif status == 'watching' and movie_id not in user['watching_movies']:
            user['watching_movies'].append(movie_id)
        elif status == 'wishlist' and movie_id not in user['wishlist_movies']:
            user['wishlist_movies'].append(movie_id)

        save_json('users.json', users)
        return JsonResponse({"message": "Movie status updated"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)


# Profile view showing watched, wishlist, and reviewed movies
def profile(request, user_name):
    users = load_json('users.json')
    movies = load_json('movies.json')
    reviews = load_json('reviews.json')

    user = next((u for u in users if u['user_name'] == user_name), None)

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    watched_movies = [m for m in movies if m['id'] in user['watched_movies']]
    wishlist_movies = [m for m in movies if m['id'] in user['wishlist_movies']]
    reviewed_movies = [m for m in movies if any(r['user_name'] == user_name and r['movie_id'] == m['id'] for r in reviews)]

    return JsonResponse({
        "watched_movies": watched_movies,
        "wishlist_movies": wishlist_movies,
        "reviewed_movies": reviewed_movies
    }, status=200)


# Suggestions view based on favorite tags


@csrf_exempt
def suggestions(request, user_name):
    movies = load_json('movies.json')
    users = load_json('users.json')
    reviews = load_json('reviews.json')

    user = next((u for u in users if u['user_name'] == user_name), None)

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    suggested_movies = [movie for movie in movies if any(tag in movie['tags'] for tag in user['favorite_tags'])]

    for movie in suggested_movies:
        movie_reviews = [review for review in reviews if review['movie_id'] == movie['id']]
        movie['review_count'] = len(movie_reviews)

    return JsonResponse({"suggested_movies": suggested_movies}, status=200)
