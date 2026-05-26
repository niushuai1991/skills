# Configuration Property Changes (Spring Boot 2.x → 3.0)

## Renamed Properties

| Old Property | New Property | Notes |
|---|---|---|
| `server.max-http-header-size` | `server.max-http-request-header-size` | Only applies to request headers now |
| `spring.redis.*` | `spring.data.redis.*` | Redis auto-config requires Spring Data |
| `spring.data.cassandra.*` | `spring.cassandra.*` | `spring.data` prefix reserved for Spring Data |
| `management.metrics.export.prometheus.*` | `management.prometheus.metrics.export.*` | Metrics export path restructured |
| `management.metrics.export.influx.*` | `management.influx.metrics.export.*` | Same pattern |
| `management.metrics.export.datadog.*` | `management.datadog.metrics.export.*` | Same pattern |
| `management.metrics.export.newrelic.*` | `management.newrelic.metrics.export.*` | Same pattern |
| `management.metrics.export.graphite.*` | `management.graphite.metrics.export.*` | Same pattern |
| `management.metrics.export.ganglia.*` | `management.ganglia.metrics.export.*` | Same pattern |
| `spring.security.saml2.relyingparty.registration.*.identity-provider` | `.asserting-party` | SAML2 config path change |

## Removed Properties

| Property | Notes |
|---|---|
| `spring.jta.atomikos.*` | Atomikos support removed |
| `spring.activemq.*` | ActiveMQ support removed |
| `spring.solr.*` | Solr support removed (Jetty 11 incompatibility) |
| `spring.session.store-type` | Store type auto-detection, no manual override |
| `spring.jta.log-dir` | Removed with Atomikos |
| `spring.jta.transaction-manager-id` | Removed with Atomikos |
| `spring.jpa.hibernate.use-new-id-generator-mappings` | Hibernate 6.1 no longer supports old generators |
| `spring.elasticsearch.rest.*` | Replaced by new Elasticsearch Java client properties |

## Config Data Changes (2.4+)

| Old Syntax | New Syntax | Notes |
|---|---|---|
| `spring.profiles: "name"` (in YAML doc) | `spring.config.activate.on-profile: "name"` | Profile activation in multi-document YAML |
| `spring.profiles` + `spring.profiles.include` | `spring.profiles.group.<name>` | Use profile groups instead |

## New Notable Properties (3.0+)

| Property | Notes |
|---|---|
| `spring.security.filter.dispatcher-types` | Configure security filter dispatch types (default: all) |
| `management.endpoints.jackson.isolated-object-mapper` | Separate ObjectMapper for actuator (default: true) |
| `management.endpoint.env.show-values` | Control env endpoint value display (NEVER/ALWAYS/WHEN_AUTHORIZED) |
| `management.endpoint.configprops.show-values` | Same for configprops endpoint |
| `logging.pattern.dateformat` | Restore old date format if needed |
