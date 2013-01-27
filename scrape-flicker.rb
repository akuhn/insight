require 'rubygems'
require 'geocoder'
require 'open-uri'
require 'json'
require 'pry'

# Monkey patching (fold)

class Hash
  def method_missing(sym,*args)
    fetch(sym){fetch(sym.to_s){super}}
  end
end

# (end)

class Flicker
  def self.photos_search(parameters)
    token = JSON.parse(File.read('flicker-api-key.json'), :symbolize_names => true)
    endpoint = 'http://api.flickr.com/services/rest/'
    parameters = {
      :method => 'flickr.photos.search',
      :api_key => token[:key],
      :format => 'json',
      :nojsoncallback => 1,
      :per_page => 500,
      #
      :sort => 'date-taken-desc',
      :radius => 10,
      :extras => 'description,date_upload,date_taken,owner_name,geo,tags,machine_tags,views,url_s',
      #
    }.update(parameters)
    p call = "#{endpoint}?#{parameters.collect{|each|each.join('=')}.join('&')}"
    data = JSON.parse(open(call).read, :symbolize_names => true)
  end
end

Vancouver = { :lat => 49.25, :lon => -123.1 }
params = Vancouver.update(
  :max_taken_date => '2013-01-01+00:00:00',
  :min_taken_date => '2010-01-01+00:00:00'
)
data = Flicker.photos_search(params)
p data
puts "Found #{data.photos.total} photos (#{data.photos.pages} pages)"
for page in 1 .. data.photos.pages do
  puts "Fetching page #{page}..."
  params.update(:page => page)
  data = Flicker.photos_search(params)
  p data.stat
  p data.photos.photo.first.datetaken
  File.open("vancouver-3y-p#{'%03d' % page}.json",'w'){|f|f.write(JSON.dump(data))}
end
