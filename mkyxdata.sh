advertisers="1458 2261 2997 3386 3476 2259 2821 3358 3427"
# advertisers="2997"

for advertiser in $advertisers; do
    echo $advertiser
    python python/mkyx.py $advertiser/train.log.txt $advertiser/test.log.txt $advertiser/train.yx.txt $advertiser/test.yx.txt $advertiser/featindex.txt
done

