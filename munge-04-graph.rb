require 'rubygems'
require 'geocoder'
require 'mongo'
require 'pry'
require :monkey_patching.to_s

db = Mongo::MongoClient.new['4h']
g = db['graph'].find_one(:city => 'vancouver')

sights = g.sights.collect{|name,durations|
  a = durations.reject{|m|m==0}.sort
  [(a[0.75*a.size].to_i/60/5.0).ceil*5,name]
}

sights.sort_by(&:first).reverse.each{|t,name|
  puts "#{t}\t#{name}"
}