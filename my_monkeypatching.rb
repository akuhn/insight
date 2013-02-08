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
    first
  end
  def sample
    shuffle.first
  end
  def average
    inject(&:+) / size
  end
  def percentile(f)
    return nil if empty?
    sorted = self.sort
    n = f.to_f * (self.size - 1)
    a,b = n.floor,n.ceil
    return sorted[a] if a == b
    (b-n) * sorted[a] + (n-a) * sorted[b]
  end
  def hash_by
    h = Hash.new(0)
    each{|each|h[yield(each)]=each}
    return h
  end
end

class Array
  def but_last
    self[0...-1]
  end
end

# (end)