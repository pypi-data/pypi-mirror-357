from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter


class DNSRecordA(BaseModel, frozen=True):
    type: Literal["A"]
    address: str = Field(..., description="IPv4 address")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordAAAA(BaseModel, frozen=True):
    type: Literal["AAAA"]
    address: str = Field(..., description="IPv6 address")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordALIAS(BaseModel):
    type: Literal["ALIAS"]
    aliasName: str = Field(
        ...,
        description="Canonical (true) domain name that is used to resolve resource records. Implements CNAME-like behavior for apex domain where CNAME is not allowed",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordCAA(BaseModel):
    type: Literal["CAA"]
    flag: int = Field(
        ...,
        description="0 - no flags are set; 128 - indicates that the “critical bit” is set, and that CAs should halt and not issue a certificate if they don’t recognize the contents of the tag field",
    )
    tag: str = Field(..., description="Indicates specific actions or restrictions related to certificate issuance")
    value: str = Field(
        ..., description="Contains at most one CA identifier and optional semicolon-separated parameters"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordCNAME(BaseModel):
    type: Literal["CNAME"]
    cname: str = Field(..., description="Canonical (true) domain name that is used to resolve resource records")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordHTTPS(BaseModel):
    type: Literal["HTTPS"]
    port: str = Field(
        ...,
        description="Specifies the port number for which the HTTPS record is applicable. If specified, it must be a single wildcard (an asterisk symbol) or a string that starts with an underscore and continues with a number from 1 to 65535.",
    )
    scheme: str = Field(
        ...,
        description='Specifies the scheme over which the HTTPS record applies. It is optional if the port is not specified, otherwise it is required and must be "_https"',
    )
    svcPriority: int = Field(
        ...,
        description="The priority of this record (relative to others, with lower values preferred). A value of 0 indicates AliasMode and other values indicate ServiceMode.",
    )
    targetName: str = Field(
        ...,
        description='A fully qualified domain name (FQDN) or a single ".", either the alias target (for AliasMode) or the alternative endpoint (for ServiceMode). For AliasMode, a TargetName of "." indicates that the service is not available or does not exist. For ServiceMode, if TargetName has the value ".", then the owner name of this record is used as the effective TargetName.',
    )
    svcParams: str = Field(
        ...,
        description='A whitespace-separated list with parameters describing the alternative endpoint at TargetName (only used in ServiceMode and otherwise ignored). Each SvcParam consisting of a SvcParamKey=SvcParamValue pair or a standalone SvcParamKey. Initial keys: "mandatory", "alpn", "no-default-alpn", "port", "ipv4hint", "ech", "ipv6hint", "dohpath", "ohttp", "tls-supported-groups". Arbitrary keys can be represented using the unknown-key presentation format "keyNNNNN" where NNNNN is the numeric value of the key type without leading zeros (Number 0-65535).',
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordMX(BaseModel):
    type: Literal["MX"]
    exchange: str = Field(..., description="Mail server that accepts mail")
    preference: str = Field(..., description="Preference (distance) number of mail server")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordNS(BaseModel):
    type: Literal["NS"]
    nameserver: str = Field(..., description="Nameserver name")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordPTR(BaseModel):
    type: Literal["PTR"]
    pointer: str = Field(..., description="The domain name that corresponds to the given IP address")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordSRV(BaseModel):
    type: Literal["SRV"]
    service: str = Field(
        ...,
        description='Specifies the symbolic name of the desired service. For example, "_sip" for SIP (Session Initiation Protocol) or "_ldap" for LDAP (Lightweight Directory Access Protocol)',
    )
    protocol: str = Field(
        ..., description='Indicates the transport protocol the service uses, such as "_tcp" for TCP or "_udp" for UDP'
    )
    priority: int = Field(
        ...,
        description="An integer that indicates the priority of the target host, with lower values indicating higher priority",
    )
    weight: int = Field(
        ...,
        description="Used in conjunction with the Priority field to load balance between multiple targets with the same priority. Higher values receive more connections.",
    )
    port: int = Field(..., description="The port number on which the service is available.")
    target: str = Field(..., description="The domain name of the server providing the service.")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordSVCB(BaseModel):
    type: Literal["SVCB"]
    port: str = Field(
        ...,
        description="Specifies the port number for which the SVCB record is applicable. If specified, it must be a single wildcard (an asterisk symbol) or a string that starts with an underscore and continues with a number from 1 to 65535.",
    )
    scheme: str = Field(
        ...,
        description='Indicates the scheme over which the SVCB record applies, such as "_tcp" for TCP or "_udp" for UDP.',
    )
    svcPriority: int = Field(
        ...,
        description="The priority of this record (relative to others, with lower values preferred). When svcPriority is 0, the SVCB record is in AliasMode. Otherwise, it is in ServiceMode.",
    )
    targetName: str = Field(
        ...,
        description='A fully qualified domain name (FQDN) or a single ".", either the alias target (for AliasMode) or the alternative endpoint (for ServiceMode). For AliasMode, a TargetName of "." indicates that the service is not available or does not exist. For ServiceMode, if TargetName has the value ".", then the owner name of this record is used as the effective TargetName.',
    )
    svcParams: str = Field(
        ...,
        description='A whitespace-separated list with parameters describing the alternative endpoint at TargetName (only used in ServiceMode and otherwise ignored). Each SvcParam consisting of a SvcParamKey=SvcParamValue pair or a standalone SvcParamKey. Initial keys: "mandatory", "alpn", "no-default-alpn", "port", "ipv4hint", "ech", "ipv6hint", "dohpath", "ohttp", "tls-supported-groups". Arbitrary keys can be represented using the unknown-key presentation format "keyNNNNN" where NNNNN is the numeric value of the key type without leading zeros (Number 0-65535).',
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordTLSA(BaseModel):
    type: Literal["TLSA"]
    port: str = Field(
        ...,
        description="Specifies the port number for which the TLSA record is applicable. Should be equal asterisk or must start with an underscore and have a number between 1 and 65535",
    )
    protocol: str = Field(
        ...,
        description='Indicates the protocol over which the TLSA record applies, such as "_tcp" for TCP or "_udp" for UDP.',
    )
    usage: int = Field(..., description="Specifies how the certificate association is used")
    selector: int = Field(..., description="Specifies which part of the certificate to use")
    matching: int = Field(..., description="Defines how the certificate association is presented in the record")
    associationData: str = Field(
        ...,
        description="The actual data (hash or full certificate) that the TLSA record is associating with the domain name.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        ge=60,
        le=3600,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


class DNSRecordTXT(BaseModel):
    type: Literal["TXT"]
    value: str = Field(..., description="Text value")
    name: str = Field(
        ...,
        min_length=1,
        max_length=253,
        description="Name of resource record excluding domain name part. '@' can be used as an apex domain",
    )
    ttl: int = Field(
        ...,
        gt=0,
        description="Specifies the amount of time in seconds that a DNS record should be cached by a resolver or a caching server before it expires and needs to be refreshed from the authoritative DNS servers",
    )


DNSRecord = Annotated[
    Union[
        DNSRecordA,
        DNSRecordAAAA,
        DNSRecordALIAS,
        DNSRecordCAA,
        DNSRecordCNAME,
        DNSRecordHTTPS,
        DNSRecordMX,
        DNSRecordNS,
        DNSRecordPTR,
        DNSRecordSRV,
        DNSRecordSVCB,
        DNSRecordTLSA,
        DNSRecordTXT,
    ],
    Field(discriminator="type"),
]

DNSRecordTypeAdapter = TypeAdapter(DNSRecord)
