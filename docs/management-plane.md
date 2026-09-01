# Aspartame management plane

Aspartame will support optional administration for classrooms, families, and managed fleets without turning Sugar into a remotely controlled backdoor.

## First slice

The isolated prototype in `management/` proves health, enrollment, device status, check-in, policy, Activity catalog, and audit endpoints. It binds to `127.0.0.1` by default. No guest agent has been installed yet, and no remote shell or arbitrary command endpoint exists.

```text
administrator service
        │ authenticated enrollment/check-in
        ▼
Aspartame device agent (future)
        │ local, authorized actions
        ▼
Sugar / Activities / Arch
```

## Why separate it from Sugar?

Sugar owns the desktop interaction model, Activities, Journal, Frame, Neighborhood, and collaboration concepts. Fleet administration crosses into deployment, identity, policy, updates, and audit. Keeping that boundary explicit lets Aspartame work with Sugar without replacing it.

## Roadmap

1. Add a consent-visible device agent with least-privilege local actions.
2. Add administrator authentication and TLS deployment.
3. Add classroom groups and policy versioning.
4. Feed Activity inventory and ratings into the management dashboard.
5. Add remote assistance only as an explicit, user-visible session.

Production deployment must not use the development enrollment default, plain HTTP across a network, or unrestricted administrator tokens.
