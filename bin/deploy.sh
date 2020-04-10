#!/bin/bash
set -e

if [ "$CIRCLECI" != "true" ]; then
    echo "Please only run this script on the CircleCI build server!"
    exit 1
fi

# # Clean project root
# echo
# git clean -dfx
# echo

# # Create archive of deployment files
# echo
# DEPLOY_TMP_DIR="/tmp/deploy_root"

# rm -fr "$DEPLOY_TMP_DIR"
# mkdir -p "$DEPLOY_TMP_DIR/revcaster-extractor"

# cp deploy/Dockerrun.aws.json "$DEPLOY_TMP_DIR"

# cp -R . "$DEPLOY_TMP_DIR/revcaster-extractor"

if [ "${CIRCLE_BRANCH}" = 'master' ]; then
    echo "Updating Dockerrun.aws.json to match production image."
    sed -i "s/IMAGE_TAG_PLACEHOLDER/prod/g" /deploy/Dockerrun.aws.json

else
    echo "Updating Dockerrun.aws.json to match develop image."
    sed -i "s/IMAGE_TAG_PLACEHOLDER/dev/g" $DEPLOY_TMP_DIR/Dockerrun.aws.json
fi

pushd "$DEPLOY_TMP_DIR"
zip -r deploy.zip .
popd

cp "$DEPLOY_TMP_DIR/deploy.zip" .

rm -fr "$DEPLOY_TMP_DIR"
echo

# Upload artifact to S3
echo
if [ "$CIRCLE_BRANCH" = "master" ]; then
    aws s3 cp deploy.zip s3://revcaster.prod.deployment-artifacts/revcaster-extractor/
else
    aws s3 cp deploy.zip s3://revcaster.develop.deployment-artifacts/revcaster-extractor/
fi
echo