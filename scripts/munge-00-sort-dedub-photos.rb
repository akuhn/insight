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
#  - removing unused fields

City = 'sanfran'

def munge_photos(photos)
  keep = 
  %w{datetaken dateupload description id latitude longitude owner ownername
  place_id tags title url_q url_sq views woeid}
  reply = []
  photos.each do |photo|
    next unless photo.datetakengranularity == "0"
    next unless photo.accuracy == "16"
    photo['description'] = photo.description['_content']
    (photo.keys-keep).each{|key|photo.delete(key)}
    begin
      str = photo.datetaken
      time = str.scan(/\d+/).collect(&:to_i)
      photo['datetaken'] = Time.utc(*time).to_i
    rescue
      p photo.datetaken
    end
    reply << photo
  end
  return reply
end

def sorted_photos(date)
  ((date-1)..(date+1)).collect do |data|
    "downloads/#{City}-#{date}.json"
  end.select do |fname|
    fname.exist?
  end.collect do |fname|
    JSON.load(File.read(fname))
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