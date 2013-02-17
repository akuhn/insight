require 'rubygems'
require 'open-uri'
require 'json'
require 'date'
require 'pry'

require 'my_monkeypatching'

# Download flicker photos to downloads folder.

class Flicker
  def self.token
    JSON.parse(File.read('token-flicker.json'), :symbolize_names => true)
  end
  def self.photos_search(hash)
    endpoint = 'http://api.flickr.com/services/rest/'
    parameters = {
      :method => 'flickr.photos.search',
      :api_key => token[:key],
      :format => 'json',
      :nojsoncallback => 1,
      :per_page => 250,
      :extras => 'description,date_upload,date_taken,owner_name,geo,tags,views,url_sq,url_q'
    }
    parameters.merge!(hash)
    p call = "#{endpoint}?#{parameters.collect{|m|m.join('=')}.join('&')}"
    return JSON.parse(open(call).read, :symbolize_names => true)
  end
  def self.geo_search(city,date)
    params = {
      :lat => city[:lat],
      :lon => city[:lon],
      :radius => city[:radius],
      :sort => 'date-taken-desc',
      :min_taken_date => date.to_s,
      :max_taken_date => (date+1).to_s
    }
    # download first page
    data = photos_search(params)
    raise data.stat unless data.stat == 'ok'
    photos = data.photos.photo
    # download more pages
    for page in 2..data.photos.pages do
      params.update(:page => page)
      more = photos_search(params)
      raise more.stat unless more.stat == 'ok'
      photos.concat(more.photos.photo)
    end
    # return all photos
    return photos
  end  
end

Vancouver = { :lat => 49.25, :lon => -123.1, :radius => 15, :name => 'vancouver' }
Rome = { :lat => 41.9, :lon => 12.5, :radius => 10, :name => 'rome' }
Paris = { :lat => 48.8742, :lon => 2.3470, :radius => 10, :name => 'paris' }
Sanfran = { :lat => 37.775, :lon => -122.4183, :radius => 15, :name => 'sanfran' }


city = Sanfran

# download day by day (to avoid search limit)
a = Date.civil(2013,1,1)
b = Date.civil(2010,1,1)
a.step(b,-1) do |date|
  fname = "downloads/#{city.name}-#{date}.json"
  next if fname.exist?
  puts "Fetching #{fname}..."
  photos = Flicker.geo_search(city,date)
  File.open(fname,'w'){|f|JSON.dump(photos,f)}
end