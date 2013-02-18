require 'rubygems'
require 'geocoder'
#
require 'my_data'
require 'my_monkeypatching'

# Describe here

Paths = DB['new_paths'] # read
Points = DB['sights'] # read
Graph = DB['graph'] # write!

puts "Found #{Paths.count} paths..."
puts "Found #{Points.count} points of interest..."

def dist(a,b)
  Geocoder::Calculations.distance_between(a,b,:units=>:km) 
end

Sights = Points.find(:category => 'sights').to_a
Sights.reject!{|m|m.subcategory == 'stadium'}
Sights.reject!{|m|not m.latitude}
def Sights.nearest(lat,lon)
  l = [lat,lon]
  sight_dist = collect{|m|[m,dist(l,[m.latitude,m.longitude])]}
  return sight_dist.min{|a,b|a.last<=>b.last}
end

Paths.find do |cursor|
  edges = Hash.new{|h,k|h[k]=Hash.new{|h,k|h[k]=[]}}
  nodes = Hash.new{|h,k|h[k]=[]}
  cursor.each do |data|
    runs = []
    # for each find nearest sight 
    data.path.each{|photo|
      sight,dist = Sights.nearest(photo.latitude,photo.longitude)
      photo[:sight] = sight
      photo[:dist] = (dist*1000).to_i # km => meters
      photo[:sight_name] = photo.dist > 100 ? nil : photo.sight.name
    }
    # group by sight into runs
    t = data.path.split_where{|a,b|a.sight_name != b.sight_name}
    t = t.reject{|g|g.any.sight_name.nil?}
    # for each run collect time at sight
    t.each{|g|
      nodes[g.any.sight_name] << g.last.datetaken - g.first.datetaken
    }
    # for each two runs collect time between sights
    t.each_cons(2){|a,b|
      next if a.any.sight_name == b.any.sight_name
      edges[a.any.sight_name][b.any.sight_name] << b.first.datetaken - a.last.datetaken
    }
  end
  # Visting time at sights: 75 percentile excluding zeros 
  nodes.keys.each do |key|
    nodes[key] = nodes[key].reject(&:zero?)
  end
  h = Sights.hash_by(&:name)
  edges.keys.each do |a,more|
    aa = h[a]
    edges[a].keys.each do |b|
      bb = h[b]
      s = dist([aa.latitude,aa.longitude],[bb.latitude,bb.longitude]) # km
      edges[a][b] = edges[a][b].reject{|t|
        t = t / 3600.0 # h
        v = s / t # km/h
        v > 50.0
      }
    end
  end
  p data = {
    :edges => edges,
    :nodes => nodes,
    :city => 'vancouver'
  }
  Graph.insert(data)
end

puts :done

__END__
