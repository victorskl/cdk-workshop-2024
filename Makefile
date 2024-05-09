
build:
	@docker build -t my-app:dev .

run:
	@docker run -it --rm -p 8081:8081 my-app:dev

git-remote-add-codecommit:
	@git remote add origin codecommit::us-east-1://CICD_Workshop

git-remote-list:
	@git remote -v

git-remote-codecommit:
	@brew bundle

git-push-origin: git-remote-add-codecommit
	@git push --set-upstream origin main
