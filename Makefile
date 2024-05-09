
build:
	@docker build -t my-app:dev .

run:
	@docker run -it --rm -p 8081:8081 my-app:dev
