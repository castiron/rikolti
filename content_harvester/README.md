The Content Harvester tries to harvest any content specified within a given metadata record. Content broadly includes two different kinds of content - media and thumbnails. The Content Harvester additionally coalesces child metadata records into their parent metadata record. 

# Media

In some cases (at this point, exclusively Nuxeo), Rikolti harvests a full media file for public display in Calisphere. Calisphere is the site of record for these objects, and so we support a rich viewing experience for media files: a video player, audio player, and the open seadragon tiled image zoomer. 

If the metadata record contains a `media_source` field, the Content Harvester expects the `media_source` to be a dictionary with the keys: 
- `url` (string, required)
- `filename` (string, optional - will take last part of url string if undefined)
- `nuxeo_type` (controlled vocabulary, optional - SampleCustomPicture)
- `mimetype` ()

The content harvester will fetch a file from `media_source['url']` to the content harvester's local filesystem. If `media_source['nuxeo_type']` is provided and is `SampleCustomPicture`, the content harvester will create a jp2 derivative of the file on the content harvester's local filesystem. The content harvester then uploads either the jp2 (if one was created) or the source media file from the content harvester's local filesystem to s3, at an s3 path that includes `media_source['filename']`. Finally, the content harvester updates the metadata record to include a `media` field: a dictionary with the keys `mimetype` (string - either the original, or `image/jp2`), and `media_filepath` (string - an s3 location). 

# Thumbnails

Rikolti expects to harvest a thumbnail for all metadata records except possibly audio records (even in this case, some records may still have a thumbnail available for use). 

If the given metadata record includes a `thumbnail_source` field, the Content Harvester expects the `thumbnail_source` field to be either a string or a dictionary with the keys:
- `url` (string, required)
- `filename` (string, optional - will take last part of the url string if undefined)
- `mimetype` (string, optional - will assume 'image/jpeg' if not specified)
If `thumbnail_source` is a string, the content harvester assumes the string to be the `thumbnail_source['url']`. 

The Content Harvester will fetch a file from `thumbnail_source['url']` to the content harvester's local filesystem (if the very same file hasn't already been fetched and stored there via the media harvesting process). 

If `thumbnail_source['mimetype']` is provided and is `application/pdf`, the content harvester will create a thumbnail derivative of the first page using ImageMagick. If `thumbnail_source['mimetype']` is provided and is `video/mp4`, ffprobe is used to find the center timestamp of the video, and ffmpeg is used to get the frame at the center timestamp. If `thumbnail_source['mimetype']` is provided, and is not `application/pdf`, `video/mp4` or `image/jpeg`, the content harvester will raise an UnsupportedMimetype error. 

The content harvester uploads either the original fetched thumbnail or (in the case of pdfs and video files) the produced derivative from the content harvester's local file system to s3 at an s3 path that includes `thumbnail_source['filename']`. Finally, the content harvester updates the metadata record with a `thumbnail` field: a dictionary with the keys `mimetype` (string - currently always `image/jpeg`), and `thumbnail_filepath` (string - an s3 location). 

# Child Metadata Records

The above media and thumbnail fetching processes are enacted upon child metadata records which, up to this point, are treated the same as a regular metadata record. After the above media and thumbnail fetching processes are enacted, the content harvester creates a list of child metadata records and updates the parent metadata record to include a field `children`, where that list is stored. 

# Settings

You can bypass uploading to s3 by setting `settings.CONTENT_DEST == 'local'`. This is useful for local development and testing. This will set the metadata records' `media['media_filepath']` and `thumbnail['thumbnail_filepath']` to a local filepath. 

# Local Development

docker build -t content_harvester .
docker compose run --rm content_harvester https://registry.cdlib.org/api/v1/rikoltimapper/26147/?format=json

--rm flag removes the container after run.

default entrypoint is `by_registry_endpoint.py` 

requires an env.local adjacent to the docker-compose in order to run (check settings.py for hints on what needs to be defined in env.local)

# TODO:
- md5 the thumbnails
- change folder name "mapped_with_content"
- tune log output (this module is v. noisy currently)
- add error handling
- figure out AWS deployment (ECR, Fargate, ECS)