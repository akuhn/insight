require 'rubygems'
require 'mongo'
require 'json'
require 'date'
#
require 'my_monkeypatching'

# Enter downloades flicker photos in mongo:
#  - unpacking description
#  - parsing datetaken as utime
#  - sorting by datetaken
#  - delete keys we're not looking for

City = 'sanfran'

def munge_photos(photos)
  keep = 
  %w{datetaken dateupload description id latitude longitude owner ownername
  place_id tags title url_q url_sq views woeid}
  reply = []
  photos.each do |photo|
    # We need dates including time of the day
    next unless photo.datetakengranularity == "0"
    # We need street level accuracy
    next unless photo.accuracy == "16"
    # Unpack description
    photo['description'] = photo.description['_content']
    # These are not the keys you're looking for 
    (photo.keys-keep).each{|key|photo.delete(key)}
    # Parse datetaken into utime, gloss over errors
    begin
      photo['datetaken'] = parse_time(photo.datetaken).to_i
    rescue
      p photo.datetaken
    end
    reply << photo
  end
  return reply
end

def sorted_photos(date)
  # Load three days to account for flickr API glitches
  ((date-1)..(date+1)).collect do |data|
    "downloads/#{City}-#{date}.json"
  # Gloss over missing files
  end.select do |fname|
    fname.exist?
  # Read files 
  end.collect do |fname|
    JSON.load(File.read(fname))
  # Select given day only  
  end.flatten.select do |photo|
    photo.datetaken[0...10] == date.to_s
  end.sort_by(&:datetaken)
end

a = Date.civil(2010,1,1)
b = Date.civil(2013,1,1)

db = Mongo::MongoClient.new()[City]
db_photos = db['photos']
a.step(b,1) do |date|
  puts date
  photos = sorted_photos(date)
  photos = munge_photos(photos)
  photos.each do |photo|
    db_photos.insert(photo)
  end
end

puts :done

keys =
%w{accuracy context datetaken datetakengranularity dateupload description farm
geo_is_contact geo_is_family geo_is_friend geo_is_public height_q height_sq id
isfamily isfriend ispublic latitude longitude owner ownername place_id secret
server tags title url_q url_sq views width_q width_sq woeid}