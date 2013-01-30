require 'rubygems'
require 'time'
require 'date'
require 'mongo'
require 'json'
require 'set'
require 'pry'

# Monkey patching (fold)

class Hash
  def method_missing(sym,*args)
    fetch(sym){fetch(sym.to_s){super}}
  end
  def id
    fetch(:id){fetch('id'){raise}}
  end
end

module Enumerable
  def fmap#{|each|}
    ary=[];each{|each|ary.concat(yield(each))};ary
  end
  def count_by
    h = Hash.new(0)
    each{|each|h[yield(each)]+=1}
    h.sort_by{|k,count|count}.reverse
  end
  def split_where # {|a,b|}
    runs = [[first]]
    each_cons(2){|a,b|
      runs << [] if yield(a,b)
      runs.last << b
    }
    return runs 
  end
  def any
    shuffle.first
  end
end

# (end)

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
  next if days > 30
  
  paths = photos.sort_by(&:datetaken).split_where{|a,b|(b.datetaken-a.datetaken)>1*360}
  paths = paths.select{|m|m.size > 3}
  paths.each do |path|
    p user
    p path.each_cons(2).collect{|a,b|(b.datetaken-a.datetaken).to_i}
    Paths.insert(:path => path)
    p Paths.count
  end
end