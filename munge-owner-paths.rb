require 'rubygems'
require 'time'
require 'date'
require 'mongo'
require 'json'
require 'set'
require 'pry'

require :monkey_patching.to_s

module Parameters
  DAYS_IN_TOWN = 21
  PATH_SEPARATOR = 8 * 360 # 4 hours
end

mongo = Mongo::MongoClient.new()
db = mongo['4h']
All = db['vancouver']
Paths = db['paths']

puts "Found #{All.size} entries."

All.distinct(:owner).each do |user|
  photos = All.find({ :owner => user }).to_a
  photos.each{|m|m['datetaken']=Time.parse(m.datetaken).to_i}
  # photos.collect(&:datetaken).collect(&:mday).uniq.size
  
  days = (photos.last.datetaken - photos.first.datetaken) / 86400
  next if days > Parameters::DAYS_IN_TOWN
  
  paths = photos.sort_by(&:datetaken).split_where{|a,b|(b.datetaken-a.datetaken)> Parameters::PATH_SEPARATOR}
  paths = paths.select{|m|m.size > 3}
  paths.each do |path|
    p user
    p path.each_cons(2).collect{|a,b|(b.datetaken-a.datetaken).to_i}
    Paths.insert(:path => path)
    p Paths.count
  end
end