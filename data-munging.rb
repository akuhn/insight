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

photos = []

File.open('data/vancouver-3y.json') do |f|
  f.each{|line|
    photos << JSON.parse(line,:symbolize_names => true)
    break if photos.size > 50000
  }
end

puts photos.size

photos = photos.uniq
photos.each{|m|m[:description]=m[:description][:_content]}
photos.each{|m|m[:tags]=m[:tags].split}
photos.each{|m|m[:datetaken]=Time.parse(m[:datetaken])}

[:geo_is_public, :views, :datetakengranularity, :machine_tags, :dateupload, :owner, :latitude, :secret, :geo_is_contact, :ownername, :width_s, :geo_is_friend, :woeid, :height_s, :datetaken, :title, :place_id, :description, :isfamily, :ispublic, :accuracy, :context, :geo_is_family, :farm, :url_s, :id, :server, :isfriend, :tags, :longitude]

puts photos.size

def locals_and_tourists(photos)
  users = photos.group_by(&:owner).values
  p users.collect{|us|us.collect{|m|m.datetaken.yday}.uniq.size}
end
locals_and_tourists(photos)

break

users = photos.group_by(&:owner).values.sort_by(&:size).reverse.take(20)

trails = photos.group_by(&:owner).values.fmap{|us|us.sort_by(&:datetaken).split_where{|a,b|(b.datetaken - a.datetaken) > 360}.select{|ms|ms.size>3}}.sort_by(&:size).reverse

trails.each do |ms|
  p ms.first.owner
  p '-' * 40
  p ms.size
  puts (ms.last.datetaken - ms.first.datetaken).to_s << " sec"
  puts Geocoder::Calculations.distance_between(
    [ms.collect(&:latitude).min,ms.collect(&:longitude).min],
    [ms.collect(&:latitude).max,ms.collect(&:longitude).max],
    :units => :km).to_s << " km"
  p ms.each_cons(2).collect{|a,b|(b.datetaken-a.datetaken).to_i}
  p ms.collect(&:tags).join(' ').scan(/[a-zA-Z]+/).uniq.sort.join(' ')
  puts ms.take(10).collect(&:title).reject(&:empty?).compact
  puts ms.take(10).collect(&:description).reject(&:empty?).compact
end


exit

us = users.any

p us.first.ownername

# p us.sort_by(&:datetaken).

trails = us.sort_by(&:datetaken).split_where{|a,b|(b.datetaken - a.datetaken) > 360}

