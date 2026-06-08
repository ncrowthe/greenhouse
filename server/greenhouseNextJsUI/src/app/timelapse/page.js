'use client';

import React, { useState, useEffect } from 'react';

import { Knob } from 'primereact/knob';
const config = require('../config/config.js');
import { IoRainyOutline } from 'react-icons/io5';
import { Button, Grid, Column, Slider } from '@carbon/react';
import '@carbon/charts-react/styles.css';
const endpoints = require('../config/endpoints.js');

function Timelapse() {
  const [camState, setCamState] = useState('OFF');
  const [camTimelapse, setCamTimelapse] = useState(0);
  const [imageSize, setImageSize] = useState('2592x1944');

  const [selectedEnv, setSelectedEnv] = useState(config.getEnv());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState();

  const setEnv = async (event) => {
    console.log('Event: ' + JSON.stringify(event));
    config.setEnv(event);
    setLoading(true);
    await getConfigData(event);
    setLoading(false);
  };

  const handleOnSubmit = (event) => {
    // Prevent default refresh
    event.preventDefault();

    writeConfig(event);
  };

  function writeConfig(event) {
    const [camImageXPixels, camImageYPixels] = imageSize
      .split('x')
      .map((value) => Number(value));

    let configData = JSON.stringify({
      camState: camState,
      camTimelapse: camTimelapse,
      camImageXPixels: camImageXPixels,
      camImageYPixels: camImageYPixels,
    });

    console.log(
      'Send: ' + configData + ' to env: ' + JSON.stringify(selectedEnv.id)
    );

    config.timelapse(configData, selectedEnv.id);
  }

  async function getConfigData(selectedEnv) {
    await config
      .getConfigData(selectedEnv)
      .then((configData) => {
        console.log('Config*******' + JSON.stringify(configData));
        if (configData) {
          setCamState(configData.camState);
          setCamTimelapse(configData.camTimelapse);

          if (configData.camImageXPixels && configData.camImageYPixels) {
            setImageSize(
              `${configData.camImageXPixels}x${configData.camImageYPixels}`
            );
          }
        }
      })
      .catch((err) => {
        console.log(err);
        return <Grid className="config-page">Error</Grid>;
      });

    setLoading(false);
  }

  useEffect(() => {
    getConfigData(selectedEnv);
  }, []);

  if (loading) {
    return <Grid className="config-page">Loading</Grid>;
  }

  if (error) {
    return `Error! ${error}`;
  }

  // Set cam buttons and highlight the one that is enabled
  let camButton = {};
  if (camState === 'ON') {
    camButton = (
      <div>
        <Button
          kind="primary"
          renderIcon={IoRainyOutline}
          inputid="cam1"
          name="camOn"
          value="ON"
          onClick={(e) => setCamState('ON')}
        >
          {' '}
          ON*
        </Button>
        <Button
          kind="tertiary"
          renderIcon={IoRainyOutline}
          inputid="cam2"
          name="camOff"
          value="OFF"
          onClick={(e) => setCamState('OFF')}
        >
          {' '}
          OFF
        </Button>
        <Button
          kind="tertiary"
          renderIcon={IoRainyOutline}
          inputid="cam3"
          name="camAuto"
          value="AUTO"
          onClick={(e) => setCamState('AUTO')}
        >
          {' '}
          AUTO
        </Button>
      </div>
    );
  } else if (camState === 'OFF') {
    camButton = (
      <div>
        <Button
          kind="tertiary"
          renderIcon={IoRainyOutline}
          inputid="cam1"
          name="camOn"
          value="ON"
          onClick={(e) => setCamState('ON')}
        >
          {' '}
          ON
        </Button>
        <Button
          kind="primary"
          renderIcon={IoRainyOutline}
          inputid="cam2"
          name="camOff"
          value="OFF"
          onClick={(e) => setCamState('OFF')}
        >
          {' '}
          OFF*
        </Button>
        <Button
          kind="tertiary"
          renderIcon={IoRainyOutline}
          inputid="cam3"
          name="camAuto"
          value="AUTO"
          onClick={(e) => setCamState('AUTO')}
        >
          {' '}
          AUTO
        </Button>
      </div>
    );
  } else {
    camButton = (
      <div>
        <Button
          kind="tertiary"
          renderIcon={IoRainyOutline}
          inputid="cam1"
          name="camOn"
          value="ON"
          onClick={(e) => setCamState('ON')}
        >
          {' '}
          ON
        </Button>
        <Button
          kind="tertiary"
          renderIcon={IoRainyOutline}
          inputid="cam2"
          name="camOff"
          value="OFF"
          onClick={(e) => setCamState('OFF')}
        >
          {' '}
          OFF
        </Button>
        <Button
          kind="primary"
          renderIcon={IoRainyOutline}
          inputid="cam3"
          name="camAuto"
          value="AUTO"
          onClick={(e) => setCamState('AUTO')}
        >
          {' '}
          AUTO*
        </Button>
      </div>
    );
  }

  return (
    <Grid>
      <Column lg={16} md={8} sm={4} className="landing-page__banner">
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {config.getEnvs().map((env) => (
            <button
              key={env.id}
              onClick={() => {
                setSelectedEnv(env);
                setEnv(env);
              }}
              style={{
                padding: '16px 32px',
                fontSize: '16px',
                backgroundColor:
                  selectedEnv.id === env.id ? '#0f62fe' : '#e0e0e0',
                color: selectedEnv.id === env.id ? 'white' : 'black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: selectedEnv.id === env.id ? 'bold' : 'normal',
              }}
            >
              {env.name}
            </button>
          ))}
        </div>
      </Column>
      <Column lg={10} md={10} sm={10}>
        <br></br>
        <form onSubmit={(e) => handleOnSubmit(e)}>
          <br></br>
          <h4>Cam:</h4>
          {camButton}

          <br></br>
          <br></br>

          <h4>Timelapse (Minutes):</h4>
          <Slider
            ariaLabelInput="Lower bound"
            invalidText="Invalid value"
            labelText=""
            max={1440}
            min={0}
            step={1}
            unstable_ariaLabelInputUpper="Upper bound"
            value={camTimelapse}
            warnText="Warning message goes here"
            onChange={(e) => setCamTimelapse(e.value)}
          />

          <br></br>
          <br></br>

          <fieldset style={{ border: '1px solid #ccc', padding: '16px' }}>
            <legend>Image Size</legend>
            {['2592x1944', '1920x1080', '1280x720', '640x480'].map((size) => (
              <label
                key={size}
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="radio"
                  name="imageSize"
                  value={size}
                  checked={imageSize === size}
                  onChange={() => setImageSize(size)}
                  style={{ marginRight: '8px' }}
                />
                {size}
              </label>
            ))}
          </fieldset>

          <br></br>
          <br></br>

          <Button
            kind="primary"
            onClick={(e) => handleOnSubmit(e)}
            iconDescription="Set"
          >
            Set
          </Button>
        </form>
        <br></br>
        <br></br>
      </Column>
    </Grid>
  );
}
export default Timelapse;
