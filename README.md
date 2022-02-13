# Tools for Twitter Data

This is a start of a collection of tools to use for collecting data via the Twitter API. If you do not have a Twitter Developer account, please see the [Twitter Getting Started guide](https://developer.twitter.com/en/docs/twitter-api/getting-started/guide)

-   [Full-Archive Search](#Full-Archive-Search)

## Requirements:
* Python 3.7 or greater (preferably 3.9+)
* For the Full-Archive Search, a [Twitter Academic Research Project Developer Account](https://developer.twitter.com/en/docs/projects/overview#product-track)

## Installation
* Clone the repository, or download the .zip (and unzip)
* In your command line interface, change directory to the code
* Create a virtual environment
* Run `pip install -r requirements.txt`

## Full-Archive Search

(note: this requires a [Twitter Academic Research product track license](https://developer.twitter.com/en/docs/twitter-api/tweets/search/introduction), and uses the version 2 endpoints)

Using the [run_twitter_search_all.py](./run_twitter_search_all.py) tool, you can search for and download Twitter data directly from the [search all API endpoint](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all). The output will be written to the output directory as the raw json data as given to you by the Twitter API.

The program also checks for rate limiting and will automatically wait and retry as needed indefinitely.

### Usage:

```
python run_twitter_search_all.py -c {config.json}
```

The [config file](./config.json) has the following settings:

-   **api_key**: (required) your Twitter application API key
-   **api_secret**: (required) your Twitter application API secret key
-   **output_path**: (required) the path to write the output data. If the directory does not exist, it will be created.
-   **search_parameters**: (required) the search parameters to use. This is a json object of key/value pairs and will be pass as query parameters to the Twitter API. For the full list of parameters, see the **Query Parameters** section in the [Twitter API documentation](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all)
-   **log_to_file**: (optional) true or false. If true, it will write a log file when running under the `log_file_path`.
-   **log_file_path**: (optional) the path to write the runtime log files to. If the directory does not exist, it will be created.

## License

This software is licensed under the MIT license (see the [LICENSE](./LICENSE) file). No warranty of any kind is expressed or implied by your use of this software.

## Contact Us
Have an issue or question about this code? Let us know either in the [Issues section](https://github.com/texifter/tools-for-twitter/issues) or contact us at [github@texifter.com](mailto:github@texifter.com).
