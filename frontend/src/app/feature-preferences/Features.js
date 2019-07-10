// for dev mock

let featuresSent = [
  {name: 'Age', type: 'numeric', preferences: {zeroAllowed: false, negativeAllowed: false}},
  {name: 'Occupation', type: 'categorical', preferences: {categories: ['banker', 'engineer', 'lawyer']}},
  {name: 'ShirtsCount', type: 'numeric', preferences: {zeroAllowed: true, negativeAllowed: false}},
  {name: 'ShirtsBorrowedandLent', type: 'numeric', preferences: {zeroAllowed: true, negativeAllowed: true}},
];

let featuresReceived = [
  {name: 'Age', type: 'numeric'},
  {name: 'Occupation', type: 'categorical'},
  {name: 'ShirtsCount', type: 'numeric'},
  {name: 'ShirtsBorrowedandLent', type: 'numeric'},
];

module.exports = {sent: featuresSent, received: featuresReceived};
