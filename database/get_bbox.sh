##
echo "Create bounding box of Tanzania"
##
# Extract extent (bbox) from ogrinfo
# Bbox format: lon1 lat1 lon2 lat2
bbox_comma="$(ogrinfo -al -so TZA_adm0.geojson | grep Extent | awk -v ORS="," -v RS=")" -v FS="(" '{print $2}' | sed -r 's/,/ /g' | xargs | sed -r 's/ /,/g')"
echo $bbox_comma
bbox="$(echo $bbox_comma | sed 's/,/ /g')"
echo "Bounding Box: $bbox"
echo $bbox > bbox.txt
echo -e "Done!\n"
