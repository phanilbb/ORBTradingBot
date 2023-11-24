import requests


def find_keys_with_name(data, target_key="name"):
    result_keys = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                if isinstance(value, str) and value.startswith("#"):
                    result_keys.append(value)
            if isinstance(value, (dict, list)):
                result_keys.extend(find_keys_with_name(value, target_key))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result_keys.extend(find_keys_with_name(item, target_key))

    return result_keys


def get_trending_hashtags():
    result = []

    try:
        url = "https://twitter.com/i/api/2/guide.json"

        payload = {}
        headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cookie': '_ga=GA1.2.1873747202.1700805263; _gid=GA1.2.1982861911.1700805263; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCMnA5P%252BLAToMY3NyZl9p%250AZCIlMTA5NTlhMTMzOWJiZTBhMGU3ZjI3OGY5NjJiYzBhODk6B2lkIiViMzA5%250AZjNiNzE5N2VkZTVmN2NlY2RlNGQ5MThmYWNiMQ%253D%253D--8ac102619d1758285d3dba8ac2e2cb0a939ae45d; guest_id=v1%3A170080526395373259; g_state={"i_l":0}; kdt=OY9Uew0HNX01k5GHEMCHoNd2gjrnYcB3veihc1l5; auth_token=f24b6dab63ca42ba0e90b446ba526617b7314202; ct0=e66a34dbd9cf239266ad1bd5b73d058184cca0f1cded76ed081bd5200aa8b6ec35a3ab4a155305f0d412850b89141350024e5a2b12d605b4e932a0b503c19675fff35e146704357418e8180f020b290d; att=1-uBbvlW5UqONb9o81sdMQmTTI2F2W6mAnqIQLcQgW; guest_id_ads=v1%3A170080526395373259; guest_id_marketing=v1%3A170080526395373259; lang=en; twid=u%3D298081552; external_referer=padhuUp37zixoA2Yz6IlsoQTSjz5FgRcKMoWWYN3PEQ%3D|0|8e8t2xd8A2w%3D; des_opt_in=Y; personalization_id="v1_YvGk6VvV6xNDOjEVBO8kLg=="; ct0=a0a4c20f7b31b639053f2b4c8920b184c14e649618bffac12f5db265553ec19e2e44be9812eea745bdcde12e5b6921e68474e6ff9a0f19f82f1a8e1df53a8c9ddb8f2840a1e0d383c3836e632b776f36; guest_id=v1%3A170080780735024483; guest_id_ads=v1%3A170080780735024483; guest_id_marketing=v1%3A170080780735024483; lang=en; personalization_id="v1_T2zWBVS8yEZhG6tcTSxhdQ=="; twid=u%3D298081552',
            'x-csrf-token': 'e66a34dbd9cf239266ad1bd5b73d058184cca0f1cded76ed081bd5200aa8b6ec35a3ab4a155305f0d412850b89141350024e5a2b12d605b4e932a0b503c19675fff35e146704357418e8180f020b290d'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        result = find_keys_with_name(response.json(), target_key="name") + find_keys_with_name(response.json(),
                                                                                               target_key="trendName")
        result = list(set(result))
    except Exception as e:
        print("Failed to get trending hashtags from twitter : " + str(e))

    return result
