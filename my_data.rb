require 'rubygems'
require 'mongo'

DB = Mongo::MongoClient.new()['4h']

if __FILE__ == $0 then
  DB.collection_names.each do |each|
    puts "#{DB[each].count}\t#{each}"
  end 
end