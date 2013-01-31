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

data = []
Paths.find do |cursor|
  cursor.take(10).each do |data|
    curr = :begin
    runs = []
    data.path.each do |photo|
      point,dist = Points.nearest(photo.latitude,photo.longitude)
      key = dist > 0.1 ? nil : point.name # get poi_id from lonley planet!
      runs << {:poi=>key,:photos=>[]} if curr != key
      runs.last.photos << photo
      curr = key
    end
    runs.each do |each|
      each[:duration] = each.photos.last.datetaken - each.photos.first.datetaken
      each[:transition] = nil
    end
    runs.each_cons(2) do |a,b|
      a[:transition] = {
        :destination => b.poi,
        :duration => b.photos.first.datetaken - a.photos.last.datetaken
      }
    end
    p runs.collect(&:poi)
    p runs.collect(&:duration)
    p runs[1...-1].collect(&:transition).collect(&:duration)
  end
end


p :done
__END__
    
data.path.each do |photo| 
  loc = [photo.latitude,photo.longitude]
end
#p [xx.collect(&:last).uniq.compact.size,xx.size]
found += xx.collect(&:last).uniq.compact if xx.collect(&:last).uniq.compact.size > 1
#p xx
#p '-' * 40
#exit if (n += 1) > 50
