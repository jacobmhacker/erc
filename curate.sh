echo "URL of Reddit post: $1"

echo "Scraping Reddit page..."

python3 bin/get_post.py $1 > data/post.json
