require 'rubygems'
require 'geocoder'
require 'mongo'
require 'pry'
require :monkey_patching.to_s

def dist(a,b)
  Geocoder::Calculations.distance_between(a,b,:units=>:km)
end

mongo = Mongo::MongoClient.new()
db = mongo['4h']
Paths = db['paths']

Points = db['poi'].find(:category => 'sights').select(&:latitude)
def Points.nearest(lat,lon)
  l = [lat,lon]
  t = collect{|m|[m,dist(l,[m.latitude,m.longitude])]}
  return t.min{|a,b|a.last<=>b.last}
end

Paths.find do |cursor|
  travel = Hash.new{|h,k|h[k]=Hash.new{|h,k|h[k]=[]}}
  sights = Hash.new{|h,k|h[k]=[]}
  cursor.take(10000).each do |data|
    runs = []
    # find nearest POI 
    data.path.each{|photo|
      poi,dist = Points.nearest(photo.latitude,photo.longitude)
      photo[:poi] = poi
      photo[:dist] = (dist*1000).to_i
      photo[:poi_name] = photo.dist > 100 ? nil : photo.poi.name
    }
    # group photos by POI
    t = data.path.split_where{|a,b|a.poi_name != b.poi_name}
    t = t.reject{|g|g.any.poi_name.nil?}
    # compute duration of stay at POI
    t.collect{|g|
      sights[g.any.poi_name] << g.last.datetaken - g.first.datetaken
    }
    # computer travel time between POIs
    t.each_cons(2){|a,b|
      travel[a.any.poi_name][b.any.poi_name] << b.first.datetaken - a.last.datetaken
    }
  end
  p data = {
    :transitions => travel,
    :sights => sights,
    :city => 'vancouver'
  }
  db['graph'].insert(data)
end

p :done


__END__
