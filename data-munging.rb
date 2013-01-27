require 'rubygems'
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
  def fmap(&block)
    map(&block).flatten
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

photos = []

for date in Date.civil(2010,1,1)...Date.civil(2013,1,1) do
  fname = "vancouver-#{date}.json"
  break unless fname.exist?
  photos += JSON.parse(File.read(fname),:symbolize_names=>true)
end

photos = photos.uniq
photos.each{|m|m[:description]=m[:description][:_content]}
photos.each{|m|m[:tags]=m[:tags].split}
photos.each{|m|m[:datetaken]=Time.parse(m[:datetaken])}

[:geo_is_public, :views, :datetakengranularity, :machine_tags, :dateupload, :owner, :latitude, :secret, :geo_is_contact, :ownername, :width_s, :geo_is_friend, :woeid, :height_s, :datetaken, :title, :place_id, :description, :isfamily, :ispublic, :accuracy, :context, :geo_is_family, :farm, :url_s, :id, :server, :isfriend, :tags, :longitude]

puts photos.size

users = photos.group_by(&:owner).values.sort_by(&:size).reverse.take(20)

us = users.drop(3).first

p us.first.ownername

# p us.sort_by(&:datetaken).

trails = us.sort_by(&:datetaken).split_where{|a,b|(b.datetaken - a.datetaken) > 360}
p trails.collect{|ms|ms.each_cons(2).collect{|a,b|(b.datetaken-a.datetaken).to_i}}

p trails.select{|ms|ms.size > 3}.collect{|ms|ms.collect(&:tags).join(' ').scan(/[a-zA-Z]+/).uniq.sort.join(' ')}
