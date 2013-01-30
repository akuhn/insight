require 'rubygems'
require 'geocoder'
require 'json'
require 'time'
require 'date'
require 'pry'
require 'set'

# Monkey patching (fold)

class Hash
  def method_missing(sym,*args)
    fetch(sym){fetch(sym.to_s){super}}
  end
  def id
    fetch(:id){fetch('id'){raise}}
  end
end

class String
  def exist?
    File.exist?(self)
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

class Array
  alias :'__at__' :[]
  def [] key,*patterns
    return __at__(key,*patterns) unless (Symbol === key and not patterns.empty?)
    select{|each|patterns.any?{|p|p === each.send(key)}}
  end
end  

# (end)

for date in Date.civil(2010,1,1)...Date.civil(2013,2,1) do
  p fname = "data/vancouver-#{date}.json"
  break unless fname.exist?
  photos = JSON.parse(File.read(fname))
  File.open('data/vancouver-3y.json','a'){|f|
    photos.each{|m|f.puts(JSON.dump(m))}
  }
end
