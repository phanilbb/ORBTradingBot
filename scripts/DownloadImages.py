import requests
import os

# List of image URLs
image_urls = [
    "https://b.zmtcdn.com/data/dish_photos/9a5/3a1bcc74fe668783757541b6427e59a5.jpg",
    "https://b.zmtcdn.com/data/dish_photos/cf7/3867d0c8b45500df30d9bc1cebe1bcf7.jpg",
    "https://b.zmtcdn.com/data/dish_photos/c27/ad4f04612fd5c5606acb3265363e4c27.jpg",
    "https://b.zmtcdn.com/data/dish_photos/ed5/4647a11d80e08fe22caed6610cefded5.jpg",
    "https://b.zmtcdn.com/data/dish_photos/aa1/376613a086ae56ae8a39e388effe0aa1.jpg",
    "https://b.zmtcdn.com/data/dish_photos/3b1/3a8a9b524e6f246fac8cb12e923f83b1.jpg",
    "https://b.zmtcdn.com/data/dish_photos/293/f2dcc0f94508ad7d1e9febb38929f293.jpg",
    "https://b.zmtcdn.com/data/dish_photos/cc2/64cceed797c0544e67ca75eec6d4ecc2.jpg",
    "https://b.zmtcdn.com/data/dish_photos/041/70d85c6163240db0b80b9ba22bca5041.jpg",
    "https://b.zmtcdn.com/data/dish_photos/7d8/47b546826abad792694ddb9d8e47f7d8.jpg",
    "https://b.zmtcdn.com/data/dish_photos/432/2392197fe537f3d036a44f53b2cef432.jpg",
    "https://b.zmtcdn.com/data/dish_photos/abe/5342aa97b4043d6b7c92aacbc3c6babe.jpg",
    "https://b.zmtcdn.com/data/dish_photos/91d/178ad944fef58433dafe16f3ca66491d.jpg",
    "https://b.zmtcdn.com/data/dish_photos/7ee/cdd76c57a84b4f7110c4222f4574a7ee.jpg",
    "https://b.zmtcdn.com/data/dish_photos/da1/463d8fa6bb42f7667e8701d9746c1da1.png",
    "https://b.zmtcdn.com/data/dish_photos/c88/08f52d23eba4dc453ef97dee50383c88.jpg",
    "https://b.zmtcdn.com/data/dish_photos/021/2962a842b6987174de83436d1fc04021.jpg",
    "https://b.zmtcdn.com/data/dish_photos/18e/7c9c73a17f72307069e5a3dd43df518e.jpg",
    "https://b.zmtcdn.com/data/dish_photos/021/2962a842b6987174de83436d1fc04021.jpg",
    "https://b.zmtcdn.com/data/dish_photos/117/6af1781d831dd827c742042b41b92117.jpg",
    "https://b.zmtcdn.com/data/dish_photos/f41/90924425b49d13cbb2c3eac4fc793f41.jpg",
    "https://b.zmtcdn.com/data/dish_photos/da7/66334a1b20a5a1bc1cc8793d4f097da7.jpg",
    "https://b.zmtcdn.com/data/dish_photos/da7/66334a1b20a5a1bc1cc8793d4f097da7.jpg",
    "https://b.zmtcdn.com/data/dish_photos/4ee/9d8f03597898ee952ae41f651a6704ee.jpg",
    "https://b.zmtcdn.com/data/dish_photos/117/6af1781d831dd827c742042b41b92117.jpg",
    "https://b.zmtcdn.com/data/dish_photos/f41/90924425b49d13cbb2c3eac4fc793f41.jpg",
    "https://b.zmtcdn.com/data/dish_photos/395/2b6d8cb922b0b321ee71f1f95dda8395.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/481/6742c1634667233e951248e683736481.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/7af/def68c7300508671608701d32bb977af.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/fc4/cbff8970d2985fb5c19f3a1f10e98fc4.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/436/3fdf0f4470bcd8690810868ad464e436.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/0b5/032ee9c7c9173185faceec8347f380b5.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/da7/3b8d75402a70c4d7c9c1ae6a818a5da7.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/d96/dce1d660f7475770242e95aeb8778d96.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/72e/8d20c1bf27332f7a8611958bc738172e.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/170/01a3c842b74fad02e2237db25014b170.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/7fd/7e901ee4910d018c5610d42409f3c7fd.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/18c/684cb251899dd98579abd3361313518c.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/336/249393082a62bf59fbd656584d1de336.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/96c/3686ab6ab4d8a77cdab1f4b59f10b96c.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/481/6742c1634667233e951248e683736481.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/2d1/7342460db0108b912fc0a911d5bb52d1.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/395/2b6d8cb922b0b321ee71f1f95dda8395.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/a7d/91e1bc1f231c294751c87ab50b872a7d.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/b18/2d8ef87f6d0d010eef68448470ec5b18.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/396/bea3ef2e237211a87025e50c73925396.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/d9c/589bda7252769d68f362c3d28fd21d9c.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/984/60103b4fe70681f54d466910e105c984.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/fdf/039bef59b9f599f5afcb72af3135dfdf.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/52a/a0d777484f9b767e6e28794d3ba5652a.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/a46/8a06d573c59f2dde427a3368902f8a46.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/b83/993eb99d7d856cf717fe95ada514ab83.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/598/b4c297425112244a355a829bec6cc598.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/e22/f0c04bd4d5b2ef3a631aa44dfb97ce22.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/7f4/3aa7706ca01c3773a5740ee0f8a4a7f4.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/b83/993eb99d7d856cf717fe95ada514ab83.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/2e9/0f8db5b171c9870bea4d5ed0382492e9.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/598/b4c297425112244a355a829bec6cc598.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/e22/f0c04bd4d5b2ef3a631aa44dfb97ce22.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/8dd/b671056050b1cc301fb9188ac1b338dd.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/396/bea3ef2e237211a87025e50c73925396.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/e7a/7e39126114e15412abee0c8212b49e7a.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/d9c/589bda7252769d68f362c3d28fd21d9c.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/984/60103b4fe70681f54d466910e105c984.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/fdf/039bef59b9f599f5afcb72af3135dfdf.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/52a/a0d777484f9b767e6e28794d3ba5652a.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/22f/572c7db9ad595ad9e3100efe4c0b822f.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/7f5/6433f6df5eb586043565c27aa16a17f5.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/9bc/79d3e035899531141cc92405782a59bc.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/994/2d0c0e77f1898d6a4310f1828df66994.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/a46/8a06d573c59f2dde427a3368902f8a46.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/8cf/9e1497be285fa432923e6814938528cf.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/547/518191d6cedc865730af31ce77c21547.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/7f4/3aa7706ca01c3773a5740ee0f8a4a7f4.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/955/e6a1dc7ca2c9c209d39c1f364decd955.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/b83/993eb99d7d856cf717fe95ada514ab83.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/547/518191d6cedc865730af31ce77c21547.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/eeb/75320af085cfc84e41b93f690c166eeb.jpeg",
    "https://b.zmtcdn.com/data/dish_photos/b83/993eb99d7d856cf717fe95ada514ab83.jpeg",
]

# Folder to save images
folder_path = "downloaded_images"

# Create the folder if it doesn't exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Download images
for i, url in enumerate(image_urls):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder_path, f"image_{i}.jpg"), 'wb') as f:
            f.write(response.content)
            print(f"Image {i} downloaded successfully.")
    else:
        print(f"Failed to download image {i}. Status code: {response.status_code}")
