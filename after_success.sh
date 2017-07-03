if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
    docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS
    docker push $DOCKER_REPO
fi