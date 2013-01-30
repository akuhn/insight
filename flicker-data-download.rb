require 'rubygems'
require 'open-uri'
require 'json'
require 'date'
require 'pry'

# Monkey patching (fold)

class Hash
  def method_missing(sym,*args)
    fetch(sym){fetch(sym.to_s){super}}
  end
end

class String
  def exist?
    File.exist?(self)
  end
end

# (end)

class Flicker
  def self.photos_search(parameters)
    token = JSON.parse(File.read('flicker-api-key.json'), :symbolize_names => true)
    endpoint = 'http://api.flickr.com/services/rest/'
    params = {
      :method => 'flickr.photos.search',
      :api_key => token[:key],
      :format => 'json',
      :nojsoncallback => 1,
      :per_page => 500,
      #
      :extras => 'description,date_upload,date_taken,owner_name,geo,tags,machine_tags,views,url_s',
    }
    params.merge!(parameters)
    p call = "#{endpoint}?#{params.collect{|each|each.join('=')}.join('&')}"
    data = JSON.parse(open(call).read, :symbolize_names => true)
  end
  def self.geo_search(location,date)
    params = {
      :lat => location[:lat],
      :lon => location[:lon],
      :radius => location[:radius],
      :sort => 'date-taken-desc',
      :min_taken_date => date.to_s,
      :max_taken_date => (date+1).to_s
    }
    data = photos_search(params)
    raise data.stat unless data.stat == 'ok'
    for page in 2..data.photos.pages do
      params.update(:page => page)
      more = photos_search(params)
      raise more.stat unless more.stat == 'ok'
      data.photos.photo.concat(more.photos.photo)
    end
    return data.photos.photo
  end  
end

Vancouver = { :lat => 49.25, :lon => -123.1, :radius => 15 }
Rome = { :lat => 41.9, :lon => 12.5, :radius => 10, :name => 'rome' }
Paris = { :lat => 48.8742, :lon => 2.3470, :radius => 10, :name => 'paris' }
Sanfran = { :lat => 37.775, :lon => -122.4183, :radius => 10, :name => 'sanfran' }


city = Paris
for date in Date.civil(2010,1,1)...Date.civil(2013,1,1) do
  fname = "data/#{city.name}-#{date}.json"
  next if fname.exist?
  puts "Fetching #{fname}..."
  photos = Flicker.geo_search(city,date)
  File.open(fname,'w'){|f|JSON.dump(photos,f)}
end