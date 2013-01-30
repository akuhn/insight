require 'rubygems'
require 'mongo'
require 'json'
require 'set'
require 'monkey_patching'

mongo = Mongo::MongoClient.new()
db = mongo['4h']
Paths = db['vancouver_paths']

puts "Found #{Paths.size} entries."

p Paths.find.to_a.collect{|each|
  each.path.collect{|photo|[photo.latitude,photo.longitude]}
}