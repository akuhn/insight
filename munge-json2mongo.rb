require 'rubygems'
require 'mongo'
require 'json'

# Monkey patching (fold)

class Hash
  def method_missing(sym,*args)
    fetch(sym){fetch(sym.to_s){super}}
  end
  def id
    fetch(:id){fetch('id'){raise}}
  end
end

# end

# Create mongo database

mongo = Mongo::MongoClient.new()
db = mongo['4h']
eg = db['vancouver']

data = []
File.open('data/vancouver-3y.json') do |f|
  f.each do |line|
    data << JSON.parse(line)
  end
end

p 1

data.sort_by(&:datetaken).each do |each|
  eg.insert(each)
end

p 2