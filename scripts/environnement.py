import argparse
import subprocess
import sys

def build_image():
	subprocess.run("docker build -t local/pyramid .", shell=True)

def build_images_archs():
	subprocess.run("docker buildx build --platform linux/amd64,linux/arm64 .", shell=True)

def remove_dangling_images():
	subprocess.run("docker --log-level debug image prune -f", shell=True)

def parse_arguments():
	parser = argparse.ArgumentParser(description="Manage application environnement")
	parser.add_argument("--images-purge", action="store_true", help="Remove all Docker images without tags.")
	parser.add_argument("--build", action="store_true", help="Build docker image.")
	parser.add_argument("--build-archs", action="store_true", help="Build docker images for all supported arch.")
	return parser.parse_args()

def main():
	args = parse_arguments()
	result = True

	if args.build:
		build_image()
	elif args.build_archs:
		build_images_archs()
	elif args.images_purge:
		remove_dangling_images()
	else:
		print("No action specified. Use --help for usage information.")
		return

	if not result:
		sys.exit(1)

if __name__ == "__main__":
	main()
