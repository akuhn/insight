require 'rubygems'
require 'time'
#
require 'my_data'
require 'my_monkeypatching'

# Takes flickr photos and groups them into tourist paths.


THREE_WEEKS = 21 * 86400 # days 
EIGHT_HOURS = 8 * 3600 # hours

City = 'Vancouver' 
Vancouver = {
  'latitude' => { '$gt' => 48, '$lt' => 51},
  'longitude' => { '$gt' => -125, '$lt' => -121},
}

Photos = DB['flickr'] # read
Paths = DB[nil] # write!

puts "Found #{Photos.count} photos..."

class Hash
  # Lazely convert datetaken to unix time
  def datetaken!
    time = self['datetaken']
    return time if Numeric === time
    self['datetaken'] = Time.parse(time).to_i
  end
end

Photos.distinct(:owner,Vancouver).each do |user|
  query = { :owner => user }.merge(Vancouver)
  projection = [:latitude,:longitude,:tags,:description,:datetaken,:views,:url_s]
  photos = Photos.find(query,:fields=>projection).to_a

  # Assumes documents in flickr collection are sorted by datetaken!
  tourist = (photos.last.datetaken! - photos.first.datetaken!) < THREE_WEEKS
  next unless tourist

  paths = photos.sort_by(&:datetaken!).split_where{|a,b|(b.datetaken! - a.datetaken!) > EIGHT_HOURS}
  paths = paths.select{|m|m.size > 3}
  paths.each do |path|
    Paths.insert(:path => path, :city => City)
  end
end

puts "Inserted #{Paths.count} new #{City} paths!"

puts :done