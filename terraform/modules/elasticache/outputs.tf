output "cache_security_group_id" {
  value = aws_security_group.redis.id
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.main.cache_nodes[0].address
}
