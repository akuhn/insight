require 'rubygems'
require 'mongo'
require 'json'
require 'set'

mongo = Mongo::MongoClient.new()
db = mongo['4h']
eg = db['vancouver']

puts "Found #{eg.size} entries."

# Remove duplicate

users = eg.distinct(:owner)

p users.size
p eg.find({ :owner => users.first }).count