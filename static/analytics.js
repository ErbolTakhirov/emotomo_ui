// emotomo-ui/static/analytics.js

/**
 * Event Taxonomy v1 Tracking Wrapper
 * Supports integrating PostHog or Amplitude.
 * Fallbacks to console.log for local development and QA testing.
 */

(function(window) {
  // Config
  const IS_PROD = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
  
  // 1. Generate or Retrieve Anonymous User ID
  let anonId = localStorage.getItem('emotomo_anon_id');
  if (!anonId) {
    anonId = 'anon_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    localStorage.setItem('emotomo_anon_id', anonId);
  }

  // 2. State for Super Properties
  const superProperties = {
    anonymous_user_id: anonId,
    session_id: null,
    avatar_id: null,
    mode: null,
    character_id: null
  };

  // 3. Setup PostHog (You can uncomment this and add your key when ready)
  /*
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys onSessionId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
  
  posthog.init('<YOUR_POSTHOG_API_KEY>', { 
    api_host: 'https://eu.i.posthog.com', // or us.i.posthog.com
    loaded: function(ph) {
      ph.identify(anonId);
    }
  });
  */

  const analytics = {
    // Set properties that will be sent with every event
    setSuperProperties(props = {}) {
      Object.assign(superProperties, props);
      console.log('[Analytics] Set Super Properties:', superProperties);
      
      // If using actual SDKs, register them globally:
      // if (window.posthog) window.posthog.register(superProperties);
      // if (window.amplitude) window.amplitude.identify(new amplitude.Identify().set('session_id', props.session_id));
    },

    track(eventName, properties = {}) {
      // Merge with super properties
      const finalProps = { ...superProperties, ...properties };
      
      console.log(`[Analytics] Tracked Event: ${eventName}`, finalProps);

      // Send to PostHog
      if (typeof posthog !== 'undefined' && posthog.capture) {
        posthog.capture(eventName, finalProps);
      }
      
      // Send to Amplitude (legacy fallback if used)
      if (typeof amplitude !== 'undefined' && amplitude.track) {
        amplitude.track(eventName, finalProps);
      }
    }
  };

  // Expose to window
  window.emotomoAnalytics = analytics;
  // Overwrite existing analytics object globally to avoid breaking existing calls
  window.analytics = analytics;

})(window);
